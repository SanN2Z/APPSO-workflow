"""Independent contract checks; run outside the candidate's input directory."""
import copy
import importlib.util
import itertools
import sys


def event(i, start, end, channel='wechat'):
    return dict(id=i, start=start, end=end, channel=channel)


def main(path):
    spec = importlib.util.spec_from_file_location('candidate', path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    a = event('A', '2026-09-06T09:00:00+09:00', '2026-09-06T11:00:00+09:00')
    b = event('B', '2026-09-06T09:30:00+09:00', '2026-09-06T10:00:00+09:00')
    c = event('C', '2026-09-06T10:00:00+09:00', '2026-09-06T10:30:00+09:00')
    d = event('D', '2026-09-06T09:45:00+09:00', '2026-09-06T10:15:00+09:00', 'x')
    e = event('E', '2026-09-06T02:00:00+00:00', '2026-09-06T02:30:00+00:00')
    data = [a, b, c, d, e]
    failures = []

    def check(name, action):
        try:
            assert action(), 'unexpected result'
            print('PASS', name)
        except Exception as exc:
            failures.append(name)
            print('FAIL', name, type(exc).__name__, str(exc))

    check('all_pairs_channel_timezone_boundary', lambda: m.conflicts(data) == [['A', 'B'], ['A', 'C']])
    check('duration_sample', lambda: m.total_minutes(data) == 240)
    check('permutation_invariance', lambda: all(m.conflicts(list(p)) == [['A', 'B'], ['A', 'C']] for p in itertools.permutations(data)))
    frozen = copy.deepcopy(data)
    check('no_mutation', lambda: (m.conflicts(data), m.total_minutes(data), data == frozen)[-1])
    check('empty', lambda: m.conflicts([]) == [] and m.total_minutes([]) == 0)
    overnight = [event('N', '2026-09-06T23:30:00+09:00', '2026-09-07T00:30:00+09:00')]
    check('overnight', lambda: m.total_minutes(overnight) == 60)
    long = [event('L', '2026-09-06T09:00:00+09:00', '2026-09-07T10:00:00+09:00')]
    check('over_24h', lambda: m.total_minutes(long) == 1500)
    equivalent = [event('Z', '2026-09-06T01:00:00+00:00', '2026-09-06T02:00:00+00:00'), c]
    check('same_instant_different_offset', lambda: m.conflicts(equivalent) == [['C', 'Z']])

    def rejects(rows):
        for fn in (m.conflicts, m.total_minutes):
            try:
                fn(copy.deepcopy(rows))
            except ValueError:
                continue
            return False
        return True

    check('reject_duplicate_id', lambda: rejects([a, dict(b, id='A')]))
    check('reject_naive', lambda: rejects([event('X', '2026-09-06T09:00:00', '2026-09-06T10:00:00')]))
    check('reject_reverse', lambda: rejects([dict(a, start=a['end'], end=a['start'])]))
    check('reject_zero_duration', lambda: rejects([dict(a, end=a['start'])]))
    print(f'{12-len(failures)}/12 checks passed')
    return bool(failures)


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1]))
