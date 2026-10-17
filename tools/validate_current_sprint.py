"""Read-only checks for the 2026-10-12 sprint and its three-repo mirrors.

PASS means file consistency, never a scientific gate or human identity verdict.
Only the Python standard library is required. No files or state are written.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

MEMBERS = {'王启龙', '宁显泷', '衣思淼', '代维斯丹', '王散曼'}
TASK_STATES = {'PENDING', 'IN_PROGRESS', 'NEEDS_EVIDENCE', 'BLOCKED', 'HOLD', 'REJECTED', 'COMPLETED'}
REQUIRED_REVIEW = ('primary_evidence_ref', 'primary_evidence_sha256', 'primary_observation',
    'primary_rationale', 'negative_evidence_or_search_scope', 'ai_assistance',
    'review_version', 'cross_review_ref', 'cross_review_sha256', 'cross_reviewed_at')
PLACEHOLDERS = {'UNKNOWN', 'PENDING', 'NOT_REVIEWED', 'TODO', '待填', '待核'}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def read_csv(path):
    with Path(path).open(encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or len(set(reader.fieldnames)) != len(reader.fieldnames):
            raise ValueError(f'invalid CSV headers: {path}')
        rows = list(reader)
        if any(None in r or any(v is None for v in r.values()) for r in rows):
            raise ValueError(f'invalid CSV row width: {path}')
        return rows


def validate_tasks(rows, *, followup=False, base=None, schedule=None):
    errors = []
    field = 'html_week' if followup else 'week'
    revised=bool(schedule and schedule.get('onboarding_start')=='2026-10-12' and schedule.get('research_start')=='2026-10-19')
    weeks = (range(11,18) if followup else range(2,6)) if revised else (range(10,17) if followup else range(1,5))
    expected = {(w, member) for w in weeks for member in MEMBERS}
    expected_counter=Counter(expected)
    if revised and not followup:
        expected_counter.update((1,m) for m in MEMBERS)
        expected_counter.update([(1,'王启龙'),(1,'宁显泷')])
        onboard={'ONBOARD-Q','ONBOARD-N','ONBOARD-Y','ONBOARD-D','ONBOARD-S','ONBOARD-TOOLS','ONBOARD-ROLES'}
        if {r.get('task_id') for r in rows if str(r.get('week'))=='1'}!=onboard:
            errors.append('onboarding task IDs differ from the seven planned tasks')
    actual = []
    ids = set()
    for row in rows:
        tid = row.get('task_id', '')
        try:
            w = int(row[field])
            offset = w - 6 if followup else w - 1
            start = date(2026, 10, 12) + timedelta(weeks=offset)
            if row['start'] != start.isoformat() or row['end'] != (start + timedelta(days=6)).isoformat():
                errors.append(f'{tid}: date/week mismatch')
            actual.append((w, row['owner']))
        except (ValueError, KeyError, TypeError):
            errors.append(f'{tid}: invalid week/date/owner')
        if not tid or tid in ids:
            errors.append(f'{tid}: duplicate/missing task ID')
        ids.add(tid)
        if row.get('owner') not in MEMBERS or row.get('cross_reviewer') not in MEMBERS:
            errors.append(f'{tid}: unknown reviewer')
        if row.get('owner') == row.get('cross_reviewer'):
            errors.append(f'{tid}: self review')
        if not row.get('acceptance', '').strip() or not row.get('deliverable', '').strip():
            errors.append(f'{tid}: missing deliverable/acceptance')
        if row.get('status') not in TASK_STATES:
            errors.append(f'{tid}: unknown status')
        if row.get('status') == 'COMPLETED':
            empty = [f for f in REQUIRED_REVIEW if not row.get(f, '').strip()
                     or row.get(f, '').strip().upper() in PLACEHOLDERS]
            if empty:
                errors.append(f'{tid}: missing completion evidence: {", ".join(empty)}')
            if base is None:
                errors.append(f'{tid}: evidence base required to validate completion')
            else:
                resolved = []
                for ref, hash_field in [('primary_evidence_ref', 'primary_evidence_sha256'),
                                        ('cross_review_ref', 'cross_review_sha256')]:
                    p = Path(row.get(ref) or '__MISSING__')
                    p = p if p.is_absolute() else Path(base) / p
                    resolved.append(p.resolve())
                    if not p.is_file() or digest(p) != row.get(hash_field):
                        errors.append(f'{tid}: missing/tampered {ref}')
                if resolved[0] == resolved[1]:
                    errors.append(f'{tid}: independent review must be a separate artifact')
                try:
                    date.fromisoformat(row.get('cross_reviewed_at', '')[:10])
                except ValueError:
                    errors.append(f'{tid}: invalid review date')
    if Counter(actual) != expected_counter:
        errors.append('task coverage differs from the registered research/onboarding schedule')
    return errors


def validate(root):
    root = Path(root).resolve()
    main = root / '00-当前研究'
    refs = read_json(main / 'CURRENT_EXECUTION_20261015.json')
    errors = []
    for name, expected in refs['files'].items():
        if Path(name).name != name:
            errors.append(f'unsafe file name: {name}')
            continue
        for mirror in refs['mirror_roots']:
            p = Path(mirror) / name
            if not p.is_file() or digest(p) != expected:
                errors.append(f'missing/stale mirror: {p}')
    ref_path = main / 'CURRENT_EXECUTION_20261015.json'
    for mirror in refs['mirror_roots']:
        p = Path(mirror) / ref_path.name
        if not p.is_file() or digest(p) != digest(ref_path):
            errors.append(f'execution reference mismatch: {p}')
    selector = read_json(refs['scientific_authority_selector'])
    if selector.get('current_authority') != 'V4':
        errors.append('current authority is not V4')
    source = Path(selector['root']) / 'authority/DISCOVERY_STATE_V4.json'
    state = read_json(source)
    snapshot = read_json(main / 'CURRENT_AUDIT_20261015.json')
    if digest(source) != snapshot['source_sha256']:
        errors.append('V4 source changed; refresh observation before reusing extracted tables')
    if digest(refs['scientific_authority_selector']) != snapshot['authority_selector_sha256']:
        errors.append('authority selector changed; refresh observation')
    tasks = read_csv(main / 'CURRENT_SPRINT_TASKS_20261012.csv')
    future = read_csv(main / 'CURRENT_FOLLOWUP_TASKS_20261015.csv')
    errors += validate_tasks(tasks, base=main,schedule=refs.get('schedule_revision'))
    errors += validate_tasks(future, followup=True, base=main,schedule=refs.get('schedule_revision'))
    for t in tasks:
        for ref in t['input_refs'].split('|'):
            if not (main / ref).is_file():
                errors.append(f'{t["task_id"]}: missing input {ref}')
    inventory = read_csv(main / 'CURRENT_CANDIDATE_INVENTORY_20261015.csv')
    expected_records = {(cid, track) for track, ids in state['candidate_tracks'].items() for cid in ids}
    if Counter((r['candidate_id'], r['source_track']) for r in inventory) != Counter(expected_records):
        errors.append('inventory does not match source records')
    for row in inventory:
        c = state['candidates'].get(row['candidate_id'], {})
        identity = c.get('identity', {})
        if row['structure_key'] != identity.get('inchikey') or row['canonical_smiles'] != identity.get('smiles'):
            errors.append(f'{row["candidate_id"]}: identity differs from original')
        if Path(row['source_path']).resolve() != source.resolve() or row['source_sha256'] != digest(source):
            errors.append(f'{row["candidate_id"]}: source/hash mismatch')
        if row['source_json_pointer'] != '/candidates/' + row['candidate_id']:
            errors.append(f'{row["candidate_id"]}: invalid source pointer')
        issues = '|'.join(c.get('unresolved_issues', [])) or 'NONE_RECORDED_NOT_HUMAN_CLEARED'
        if row['unresolved_issues'] != issues or row['human_review_status'] != 'PENDING':
            errors.append(f'{row["candidate_id"]}: identity issue/human status altered')
    cards = read_csv(main / 'W1_SCORING_CARDS_20261015.csv')
    if Counter(r['candidate_id'] for r in cards) != Counter(state['candidate_tracks']['EXTERNAL_LIBRARY']):
        errors.append('MCULE scorecard IDs differ from source')
    for row in cards:
        c = state['candidates'].get(row['candidate_id'], {})
        support = c.get('computational_support', {})
        for k, value in support.get('historical_values', {}).items():
            if row.get(k) != str(value):
                errors.append(f'{row["candidate_id"]}: historical numeric value changed: {k}')
        if row['source_evidence_id'] != support.get('source_evidence_id'):
            errors.append(f'{row["candidate_id"]}: score source mismatch')
        if row['new_score'] != 'UNKNOWN' or row['total_score'] != 'NOT_COMPUTED' or row['human_review_status'] != 'PENDING':
            errors.append(f'{row["candidate_id"]}: seeded card must not invent a new score/review')
        if row['source_sha256'] != digest(source) or row['structure_key'] != c.get('identity', {}).get('inchikey'):
            errors.append(f'{row["candidate_id"]}: score identity/hash mismatch')
        if Path(row['source_path']).resolve() != source.resolve() or row['source_json_pointer'] != '/candidates/'+row['candidate_id']+'/computational_support':
            errors.append(f'{row["candidate_id"]}: invalid score source pointer')
        issues = '|'.join(c.get('unresolved_issues', [])) or 'NONE_RECORDED_NOT_HUMAN_CLEARED'
        if row['identity_issue'] != issues or row['value_class'] != 'HISTORICAL_COMPUTATIONAL_SUPPORT_ONLY':
            errors.append(f'{row["candidate_id"]}: historical score limitation lost')
    queue = read_csv(main / 'REVERSE_SCREENING_QUEUE_20261015.csv')
    expected_queue = expected_records - {(cid, 'EXTERNAL_LIBRARY') for cid in state['candidate_tracks']['EXTERNAL_LIBRARY']}
    if Counter((r['compound_id'], r['source_track']) for r in queue) != Counter(expected_queue):
        errors.append('reverse screening inputs differ from source')
    for row in queue:
        c = state['candidates'].get(row['compound_id'], {})
        identity = c.get('identity', {})
        if row['structure_key'] != identity.get('inchikey') or row['canonical_smiles'] != identity.get('smiles'):
            errors.append(f'{row["compound_id"]}: reverse identity differs from original')
        if row['week'] != ('2' if row['source_track'] == 'DRUG_REPURPOSING' else '3'):
            errors.append(f'{row["compound_id"]}: reverse track/week mismatch')
        if Path(row['source_path']).resolve() != source.resolve() or row['source_json_pointer'] != '/candidates/'+row['compound_id']:
            errors.append(f'{row["compound_id"]}: invalid reverse source pointer')
        if row['screen_status'] != 'NOT_SCREENED' or row['raw_prediction'] != 'UNKNOWN' or row['human_review_status'] != 'PENDING':
            errors.append(f'{row["compound_id"]}: seed queue incorrectly claims executed screening')
        if row['source_sha256'] != digest(source):
            errors.append(f'{row["compound_id"]}: reverse source hash mismatch')
    for row in read_csv(main / 'SOURCE_ARTIFACT_AUDIT_20261015.csv'):
        if row['availability'] == 'HASH_VERIFIED_LOCAL_COPY':
            p = Path(row['verified_local_path'])
            if not p.is_file() or digest(p) != row['recorded_sha256']:
                errors.append(f'{row["artifact_id"]}: recovered source changed')
    for name in ('W1_SCORING_TEMPLATE_20261012.csv', 'REVERSE_SCREENING_TEMPLATE_20261012.csv',
                 'SPRINT_REVIEW_RECORDS_TEMPLATE_20261015.csv'):
        read_csv(main / name)  # Checks schema shape; blank templates are allowed.
    return {'file_consistency': 'PASS' if not errors else 'FAIL', 'errors': errors,
        'tasks': len(tasks), 'followup_tasks': len(future), 'named_records': len(inventory),
        'historical_scorecards': len(cards), 'not_screened_inputs': len(queue),
        'scientific_approval': 'NOT_EVALUATED_BY_THIS_TOOL', 'human_identity_verification': 'NOT_PERFORMED'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    try:
        result = validate(args.root)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        result = {'file_consistency': 'FAIL', 'errors': [str(exc)], 'scientific_approval': 'NOT_EVALUATED_BY_THIS_TOOL'}
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return 0 if result['file_consistency'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
