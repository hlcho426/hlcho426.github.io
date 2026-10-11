import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import submit

TEST_TMP = submit.ROOT / 'output/briefing'
TEST_TMP.mkdir(parents=True, exist_ok=True)


class SubmissionBoundaryTests(unittest.TestCase):
    def test_readme_sync_updates_clean_file_with_get_only(self):
        with tempfile.TemporaryDirectory(dir=TEST_TMP) as temp, patch.object(submit, 'ROOT', Path(temp)):
            path = Path(temp) / 'README.md'
            path.write_text('old\n', encoding='utf-8')
            with patch.object(submit, 'api', return_value={'object': {'sha': 'same'}}) as api, \
                patch.object(submit, 'content', return_value='new\n'), \
                patch.object(submit.subprocess, 'run') as run:
                run.return_value.stdout = 'old\n'
                self.assertEqual(submit.sync_readme()['status'], 'readme_synchronized')
                self.assertEqual(path.read_text(), 'new\n')
                self.assertTrue(all(len(c.args) == 1 for c in api.call_args_list))

    def test_readme_sync_preserves_user_edits(self):
        with tempfile.TemporaryDirectory(dir=TEST_TMP) as temp, patch.object(submit, 'ROOT', Path(temp)):
            path = Path(temp) / 'README.md'
            path.write_text('user edit\n', encoding='utf-8')
            with patch.object(submit, 'api', return_value={'object': {'sha': 'same'}}), \
                patch.object(submit, 'content', return_value='new\n'), \
                patch.object(submit.subprocess, 'run') as run:
                run.return_value.stdout = 'old\n'
                with self.assertRaisesRegex(ValueError, 'local edits'):
                    submit.sync_readme()
                self.assertEqual(path.read_text(), 'user edit\n')

    def test_readme_sync_aborts_if_main_changes(self):
        with tempfile.TemporaryDirectory(dir=TEST_TMP) as temp, patch.object(submit, 'ROOT', Path(temp)):
            path = Path(temp) / 'README.md'
            path.write_text('old\n', encoding='utf-8')
            with patch.object(submit, 'api', side_effect=[{'object': {'sha': 'before'}}, {'object': {'sha': 'after'}}]), \
                patch.object(submit, 'content', return_value='new\n'), \
                patch.object(submit.subprocess, 'run') as run:
                run.return_value.stdout = 'old\n'
                with self.assertRaisesRegex(ValueError, 'main changed'):
                    submit.sync_readme()
                self.assertEqual(path.read_text(), 'old\n')

    def test_api_destination_is_fixed(self):
        with patch.object(submit, 'gh_json', return_value={}) as call:
            submit.api('git/trees', {'tree': []})
        self.assertEqual(call.call_args.args[:2], ('api', 'repos/hlcho426/hlcho426.github.io/git/trees'))
        self.assertEqual(call.call_args.args[2:], ('--method', 'POST'))

    def test_pending_type_pr_skips_without_remote_write(self):
        with patch.object(submit, 'gh_json', side_effect=[
            [{'headRefName': 'codex/briefing-ai-2026-10-11', 'url': 'existing'}], []
        ]), patch.object(submit, 'api') as api:
            result = submit.check_remote('ai', '2026-10-12', {}, set(), set())
        self.assertEqual(result['status'], 'skipped_existing_pr')
        api.assert_not_called()

    def test_existing_branch_is_never_overwritten(self):
        with patch.object(submit, 'gh_json', side_effect=[[], []]), patch.object(submit, 'api',
            return_value=[{'ref': 'refs/heads/codex/briefing-ai-2026-10-12'}]) as api:
            with self.assertRaisesRegex(ValueError, 'never overwrite'):
                submit.check_remote('ai', '2026-10-12', {}, set(), set())
        self.assertEqual(len(api.call_args_list), 1)
        self.assertEqual(len(api.call_args.args), 1)  # GET only

    def test_check_only_does_not_create_tree_ref_or_pr(self):
        with tempfile.TemporaryDirectory(dir=TEST_TMP) as temp, patch.object(submit, 'ROOT', Path(temp)), \
            patch.object(submit, 'load_candidates', return_value=({}, set(), set())), \
            patch.object(submit, 'check_remote', return_value={'status': 'validated'}), \
            patch.object(submit, 'api') as api:
            self.assertEqual(submit.submit('ai', check_only=True)['status'], 'validated')
            self.assertFalse(list(Path(temp).rglob('submit.lock')))
        api.assert_not_called()

    def test_same_run_lock_blocks_submission(self):
        with tempfile.TemporaryDirectory(dir=TEST_TMP) as temp, patch.object(submit, 'ROOT', Path(temp)):
            directory = Path(temp) / 'output/briefing/ai' / submit.datetime.now(submit.KST).date().isoformat()
            directory.mkdir(parents=True)
            (directory / 'submit.lock').write_text('active', encoding='utf-8')
            with patch.object(submit, 'load_candidates') as load:
                with self.assertRaises(FileExistsError):
                    submit.submit('ai')
                load.assert_not_called()
            self.assertEqual((directory / 'submit.lock').read_text(), 'active')

    def test_finish_requires_both_build_and_tests(self):
        branch = f'codex/briefing-ai-{submit.datetime.now(submit.KST).date()}'
        with patch.object(submit, 'gh_json', side_effect=[
            [{'number': 17, 'url': 'pr'}],
            {'headRefName': branch, 'headRefOid': 'sha', 'isDraft': True, 'url': 'pr',
             'statusCheckRollup': [{'name': 'build', 'conclusion': 'SUCCESS'}]}
        ]), patch.object(submit, 'api') as api, patch.object(submit.subprocess, 'run') as run:
            self.assertEqual(submit.finish('ai')['status'], 'ci_pending_or_failed')
        api.assert_not_called()
        run.assert_not_called()


if __name__ == '__main__':
    unittest.main()
