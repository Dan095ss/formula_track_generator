import sys
import os
import unittest
from datetime import datetime

sys.modules.update({
    'ldap3': __import__('unittest.mock', fromlist=['MagicMock']).MagicMock(),
})
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestParseSid(unittest.TestCase):
    def test_everyone_sid(self):
        # S-1-1-0 (Everyone): revision=1, subcount=1, ia=1, sub=0
        sid_bytes = b'\x01\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00'
        from ad_users_local import parse_sid
        self.assertEqual(parse_sid(sid_bytes), 'S-1-1-0')

    def test_empty_returns_empty(self):
        from ad_users_local import parse_sid
        self.assertEqual(parse_sid(None), '')
        self.assertEqual(parse_sid(b''), '')

    def test_string_passthrough(self):
        from ad_users_local import parse_sid
        self.assertEqual(parse_sid('S-1-5-21-100'), 'S-1-5-21-100')


import uuid as _uuid


class TestParseGuid(unittest.TestCase):
    def test_known_guid(self):
        u = _uuid.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')
        from ad_users_local import parse_guid
        self.assertEqual(parse_guid(u.bytes_le), '6ba7b810-9dad-11d1-80b4-00c04fd430c8')

    def test_empty_returns_empty(self):
        from ad_users_local import parse_guid
        self.assertEqual(parse_guid(None), '')
        self.assertEqual(parse_guid(b''), '')


class TestParseWindowsTs(unittest.TestCase):
    def test_zero_returns_empty(self):
        from ad_users_local import parse_windows_ts
        self.assertEqual(parse_windows_ts(0), '')
        self.assertEqual(parse_windows_ts(None), '')

    def test_known_filetime(self):
        # FILETIME 132539328000000000 = 2021-01-01 00:00:00
        # days from 1601-01-01 to 2021-01-01 = 153402
        # 153402 * 86400 * 10_000_000 = 132539328000000000
        from ad_users_local import parse_windows_ts
        self.assertEqual(parse_windows_ts(132539328000000000), '2021-01-01 00:00:00')

    def test_ad_never_sentinel_returns_empty(self):
        from ad_users_local import parse_windows_ts
        self.assertEqual(parse_windows_ts(9223372036854775807), '')


class TestExtractManagerCn(unittest.TestCase):
    def test_standard_dn(self):
        from ad_users_local import extract_manager_cn
        dn = 'CN=John Smith,OU=Users,DC=company,DC=local'
        self.assertEqual(extract_manager_cn(dn), 'John Smith')

    def test_empty(self):
        from ad_users_local import extract_manager_cn
        self.assertEqual(extract_manager_cn(''), '')
        self.assertEqual(extract_manager_cn(None), '')

    def test_no_cn_returns_empty(self):
        from ad_users_local import extract_manager_cn
        self.assertEqual(extract_manager_cn('OU=Users,DC=company,DC=local'), '')


class TestParseUac(unittest.TestCase):
    def test_enabled(self):
        from ad_users_local import parse_uac
        status, account_type = parse_uac(512)   # 0x200 = NORMAL_ACCOUNT
        self.assertEqual(status, 'enabled')
        self.assertEqual(account_type, 'user')

    def test_disabled(self):
        from ad_users_local import parse_uac
        status, _ = parse_uac(514)  # 512 | 2 = NORMAL_ACCOUNT | ACCOUNTDISABLE
        self.assertEqual(status, 'disabled')

    def test_none_defaults_to_enabled(self):
        from ad_users_local import parse_uac
        status, _ = parse_uac(None)
        self.assertEqual(status, 'enabled')


import uuid as _uuid2


class TestMapEntryToRow(unittest.TestCase):
    def _make_entry(self):
        guid = _uuid2.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')
        sid = b'\x01\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00'
        attrs = {
            'sAMAccountName': 'ivanov.ia',
            'userPrincipalName': 'ivanov.ia@company.local',
            'uid': 'E12345',
            'userAccountControl': 512,
            'whenCreated': '2021-01-15 10:00:00',
            'pwdLastSet': 132539328000000000,
            'displayName': 'Ivanov Ivan',
            'department': 'IT',
            'title': 'Engineer',
            'company': 'DNS',
            'manager': 'CN=Petrov P,OU=Managers,DC=company,DC=local',
            'extensionAttribute12': 'Moscow',
            'extensionAttribute5': 'MS',
            'extensionAttribute8': 'PC-IVANOV',
            'extensionAttribute10': 'TYPE=employee',
            'description': 'Regular user',
        }
        raw_attrs = {
            'objectSid': [sid],
            'objectGUID': [guid.bytes_le],
        }
        return attrs, raw_attrs

    def test_row_keys(self):
        from ad_users_local import map_entry_to_row, CSV_COLUMNS
        attrs, raw_attrs = self._make_entry()
        row = map_entry_to_row(attrs, raw_attrs)
        for col in CSV_COLUMNS:
            self.assertIn(col, row, f"Missing column: {col}")

    def test_row_values(self):
        from ad_users_local import map_entry_to_row
        attrs, raw_attrs = self._make_entry()
        row = map_entry_to_row(attrs, raw_attrs)
        self.assertEqual(row['sAMAccountName'], 'ivanov.ia')
        self.assertEqual(row['source'], 'AD')
        self.assertEqual(row['status'], 'enabled')
        self.assertEqual(row['SID'], 'S-1-1-0')
        self.assertEqual(row['GUID'], '6ba7b810-9dad-11d1-80b4-00c04fd430c8')
        self.assertEqual(row['manager'], 'Petrov P')
        self.assertEqual(row['location'], 'Moscow')
        self.assertEqual(row['EA5'], 'MS')


class TestStrAndFirstRaw(unittest.TestCase):
    def test_str_none(self):
        from ad_users_local import _str
        self.assertEqual(_str(None), '')

    def test_str_list_first(self):
        from ad_users_local import _str
        self.assertEqual(_str(['hello', 'world']), 'hello')

    def test_str_empty_list(self):
        from ad_users_local import _str
        self.assertEqual(_str([]), '')

    def test_str_datetime(self):
        from ad_users_local import _str
        self.assertEqual(_str(datetime(2021, 6, 15, 12, 0, 0)), '2021-06-15 12:00:00')

    def test_str_int(self):
        from ad_users_local import _str
        self.assertEqual(_str(42), '42')

    def test_first_raw_none(self):
        from ad_users_local import _first_raw
        self.assertEqual(_first_raw(None), b'')

    def test_first_raw_bytes(self):
        from ad_users_local import _first_raw
        self.assertEqual(_first_raw(b'\x01\x02'), b'\x01\x02')

    def test_first_raw_list(self):
        from ad_users_local import _first_raw
        self.assertEqual(_first_raw([b'\xAB\xCD']), b'\xAB\xCD')

    def test_first_raw_empty_list(self):
        from ad_users_local import _first_raw
        self.assertEqual(_first_raw([]), b'')


if __name__ == '__main__':
    unittest.main()
