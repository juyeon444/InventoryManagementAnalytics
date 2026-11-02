import ast
import contextlib
import io
from pathlib import Path
import unittest
from unittest.mock import MagicMock, patch
from password_security import hash_password, verify_password
from migrate_passwords import migrate

ROOT = Path(__file__).resolve().parents[1]
GUI = (ROOT / 'auth').exists()

def method(path, name):
    tree = ast.parse((ROOT / path).read_text())
    node = next(n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name)
    env = dict(hash_password=hash_password, verify_password=verify_password, QMessageBox=MagicMock(), QTableWidgetItem=lambda value: value, Qt=MagicMock(), Error=Exception, get_valid_int=lambda _: 1)
    connection = MagicMock()
    env['db'] = MagicMock()
    env['db'].get_db_connection.return_value = connection
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(path), 'exec'), env)
    return env[name], env, connection

class PasswordTests(unittest.TestCase):
    def test_hash_roundtrip_salt_unicode_and_wrong_password(self):
        password = ' 비밀번호 $ 123 '
        a, b = hash_password(password), hash_password(password)
        self.assertNotEqual(a, b)
        self.assertTrue(verify_password(password, a))
        self.assertFalse(verify_password(password.strip(), a))
        self.assertLess(len(a), 255)

    def test_plaintext_malformed_and_empty(self):
        for value in [None, '', 'legacy', 'pbkdf2_sha256$9999999999$x$x', 'pbkdf2_sha256$600000$xx$xx']:
            self.assertFalse(verify_password('legacy', value))
        with self.assertRaises(ValueError): hash_password('')

    def test_registration_writes_hash(self):
        if GUI:
            f, env, conn = method('auth/register.py', 'register_user')
            widget = MagicMock()
            for field in ['username','password','email','first_name','last_name','phone']:
                getattr(widget, field+'_input').text.return_value = 'example'
            conn.cursor.return_value.fetchone.return_value = None
            f(widget)
        else:
            f, env, conn = method('users.py', 'create_user')
            with patch('builtins.input', return_value='example'): f(conn)
        query, values = conn.cursor.return_value.execute.call_args.args
        self.assertIn('username, password, email', query)
        self.assertTrue(verify_password('example', values[1]))
        conn.commit.assert_called_once()

    def test_password_change(self):
        if GUI:
            f, env, conn = method('customer_site/my_account.py', 'save_changes')
            widget = MagicMock()
            for field in ['password','email','first_name','last_name','phone']:
                getattr(widget, field+'_input').text.return_value = 'changed'
            f(widget)
            query, values = conn.cursor.return_value.execute.call_args.args
            encoded = values[0]
        else:
            f, env, conn = method('users.py', 'update_user_password')
            with patch('builtins.input', return_value='changed'): f(conn)
            query, values = conn.cursor.return_value.execute.call_args.args
            encoded = values[0]
        self.assertTrue(verify_password('changed', encoded))
        self.assertFalse(verify_password('old', encoded))
        conn.commit.assert_called_once()

    def test_user_lookup_does_not_fetch_credentials(self):
        paths = [('admin/user_management.py','load_users'), ('customer_site/my_account.py','load_user_info'), ('admin/admin_management.py','load_admins')] if GUI else [('users.py','read_all_users'),('users.py','read_user_by_user_id')]
        for path, name in paths:
            # Locate view method names by their SELECT if naming differs.
            tree = ast.parse((ROOT/path).read_text())
            funcs = [n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef)]
            selects = [n for n in funcs if any(isinstance(c,ast.Constant) and isinstance(c.value,str) and 'SELECT' in c.value and ('FROM users' in c.value or 'FROM admins' in c.value) for c in ast.walk(n)) and ('load' in n.name or 'read' in n.name)]
            for n in selects:
                for c in ast.walk(n):
                    if isinstance(c,ast.Constant) and isinstance(c.value,str) and 'SELECT' in c.value:
                        self.assertNotIn('password', c.value.lower())
        if not GUI:
            f, env, conn = method('users.py','read_all_users')
            conn.cursor.return_value.fetchall.return_value = [dict(user_id=1,username='demo',email='a',first_name='b',last_name='c',phone_number='d',role='customer',created_at=None)]
            out=io.StringIO()
            with contextlib.redirect_stdout(out): f(conn)
            self.assertNotIn('Password',out.getvalue())
            self.assertIn('demo',out.getvalue())

    @unittest.skipUnless(GUI, 'CLI has no login UI')
    def test_login_success_failure_unknown_and_legacy(self):
        hashed = hash_password('correct')
        for stored, supplied, success in [(hashed,'correct',True),(hashed,'wrong',False),('correct','correct',False),(None,'correct',False)]:
            f, env, conn = method('auth/login.py','handle_login')
            widget = MagicMock()
            widget.username_input.text.return_value='demo'
            widget.password_input.text.return_value=supplied
            conn.cursor.return_value.fetchone.return_value = dict(username='demo',role='customer',password=stored) if stored else None
            f(widget)
            self.assertEqual(widget.loginSuccessful.emit.called,success)
            query, values = conn.cursor.return_value.execute.call_args.args
            self.assertEqual(values,('demo',))
            self.assertNotIn('AND password',query)

    @unittest.skipUnless(GUI, 'GUI edit behavior')
    def test_blank_edit_preserves_password(self):
        f, env, conn = method('customer_site/my_account.py','save_changes')
        widget=MagicMock()
        for field in ['email','first_name','last_name','phone']:
            getattr(widget,field+'_input').text.return_value='profile'
        widget.password_input.text.return_value=''
        f(widget)
        self.assertNotIn('password',conn.cursor.return_value.execute.call_args.args[0])

    def test_admin_create_hashes_and_edit_preserves_blank(self):
        if not GUI:
            f, env, conn = method('admins.py','create_admin')
            env['get_admin_level_and_department'] = lambda: ('super admin','IT')
            with patch('builtins.input',return_value='demo'): f(conn)
            self.assertTrue(verify_password('demo',conn.cursor.return_value.execute.call_args.args[1][1]))
            return
        f, env, conn = method('admin/admin_management.py','save_changes')
        widget=MagicMock();widget.current_admin_id=None
        for field in ['username','password','email','first_name','last_name','phone']:
            getattr(widget,field+'_input').text.return_value='demo'
        for field in ['role','admin_level','department']:
            getattr(widget,field+'_input').currentText.return_value='demo'
        conn.cursor.return_value.fetchone.side_effect=[{'count':0},{'count':0},{'user_id':1}]
        f(widget)
        inserts=[c.args for c in conn.cursor.return_value.execute.call_args_list if 'INSERT INTO users' in c.args[0]]
        self.assertEqual(len(inserts),1)
        self.assertTrue(verify_password('demo',inserts[0][1][1]))

    def test_migration_is_idempotent_and_conflicts_roll_back(self):
        conn=MagicMock();cur=conn.cursor.return_value
        cur.fetchone.return_value=dict(user_id=1,password=hash_password('demo'))
        self.assertEqual(migrate(conn,['demo'],True),0)
        self.assertEqual(cur.execute.call_count,1)
        conn=MagicMock();cur=conn.cursor.return_value
        cur.fetchone.return_value=dict(user_id=1,password='legacy');cur.rowcount=0
        with self.assertRaises(RuntimeError): migrate(conn,['demo'],True)
        conn.commit.assert_not_called();conn.rollback.assert_called_once()

    @unittest.skipUnless(GUI, 'GUI account views')
    def test_gui_account_views_execute_without_credentials(self):
        for path, name, table in [('admin/user_management.py','load_users','user_table'),('admin/admin_management.py','load_admins','admin_table'),('customer_site/my_account.py','load_user_info','user_table')]:
            tree=ast.parse((ROOT/path).read_text())
            # Identify the existing load method without depending on its public name.
            candidates=[n.name for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name.startswith('load') and any(isinstance(c,ast.Constant) and isinstance(c.value,str) and 'SELECT' in c.value and ('FROM users' in c.value or 'FROM admins' in c.value) for c in ast.walk(n))]
            self.assertTrue(candidates)
            f, env, conn=method(path,candidates[0])
            widget=MagicMock()
            row=dict(user_id=1,username='demo',email='a',first_name='b',last_name='c',phone_number='d',role='admin',created_at=None,admin_id=1,admin_level='super admin',department='IT')
            conn.cursor.return_value.fetchall.return_value=[row]
            conn.cursor.return_value.fetchone.return_value=row
            f(widget)
            self.assertTrue(getattr(widget,table).setItem.called)
            for call in conn.cursor.return_value.execute.call_args_list:
                self.assertNotIn('password',call.args[0].lower())

    def test_migration_dry_run_apply_and_rollback(self):
        for apply in [False,True]:
            conn=MagicMock(); cur=conn.cursor.return_value
            cur.fetchone.return_value=dict(user_id=1,password='legacy')
            cur.rowcount=1
            self.assertEqual(migrate(conn,['demo'],apply),1)
            if apply:
                self.assertTrue(verify_password('legacy',cur.execute.call_args.args[1][0]))
                conn.commit.assert_called_once()
            else:
                self.assertEqual(cur.execute.call_count,1)
                conn.rollback.assert_called_once()
        conn=MagicMock();conn.cursor.return_value.fetchone.return_value=None
        with self.assertRaises(ValueError): migrate(conn,['missing'],True)
        conn.rollback.assert_called_once();conn.commit.assert_not_called()

if __name__ == '__main__': unittest.main()
