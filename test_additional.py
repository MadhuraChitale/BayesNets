"""Additional checks; the supplied test_q1to4.py remains unchanged."""
import itertools
import math
import random

import bayesNet as bn
import factorOperations as fo
import inference


def check():
    rng = random.Random(537)
    comparisons = 0
    # A collider and a tail exercise several elimination orders and evidence sets.
    domains = {v: [0, 1] for v in 'ABCD'}
    edges = [('A', 'C'), ('B', 'C'), ('C', 'D')]
    for trial in range(10):
        net = bn.constructEmptyBayesNet(list(domains), edges, domains)
        for variable in domains:
            parents = net.inEdges()[variable]
            cpt = bn.Factor([variable], parents, domains)
            for values in itertools.product([0, 1], repeat=len(parents)):
                assignment = dict(zip(sorted(parents), values))
                p = rng.uniform(0.05, 0.95)
                for value in [0, 1]:
                    cpt.setProbability(dict(assignment, **{variable: value}), p if value else 1-p)
            net.setCPT(variable, cpt)
        for query, evidence in [(['A'], {'D': 1}), (['A', 'B'], {'D': 0}),
                                (['D'], {}), (['A'], {})]:
            expected = inference.inferenceByEnumeration(net, query, evidence)
            hidden = sorted(set(domains) - set(query) - set(evidence))
            for order in itertools.permutations(hidden):
                calls = []
                actual = inference.inferenceByVariableEliminationWithCallTracking(calls)(
                    net, query, evidence, list(order))
                assert actual.unconditionedVariables() == expected.unconditionedVariables()
                assert actual.conditionedVariables() == expected.conditionedVariables()
                for assignment in expected.getAllPossibleAssignmentDicts():
                    assert math.isclose(actual.getProbability(assignment),
                                        expected.getProbability(assignment), abs_tol=1e-12)
                assert [v for op, v in calls if op == 'join'] == list(order)
                for i, (op, variable) in enumerate(calls):
                    if op == 'eliminate':
                        assert calls[i-1] == ('join', variable)
                comparisons += 1
            default = inference.inferenceByVariableElimination(net, query, evidence, None)
            for assignment in expected.getAllPossibleAssignmentDicts():
                assert math.isclose(default.getProbability(assignment),
                                    expected.getProbability(assignment), abs_tol=1e-12)

    # Independent hidden root must be joined, discarded, and never eliminated.
    net = bn.constructEmptyBayesNet(['A', 'B'], [], domains)
    for variable in ['A', 'B']:
        cpt = bn.Factor([variable], [], domains)
        for value in [0, 1]:
            cpt.setProbability({variable: value}, 0.5)
        net.setCPT(variable, cpt)
    calls = []
    result = inference.inferenceByVariableEliminationWithCallTracking(calls)(net, ['A'], {}, ['B'])
    assert calls == [('join', 'B')]
    assert result.getProbability({'A': 1}) == 0.5

    # General factors may be unnormalized and retain conditioned variables.
    f = bn.Factor(['A'], ['C'], domains)
    g = bn.Factor(['B'], ['C'], domains)
    for factor, weight in [(f, 2), (g, 3)]:
        for assignment in factor.getAllPossibleAssignmentDicts():
            factor.setProbability(assignment, weight)
    joined = fo.joinFactors([f, g])
    assert joined.conditionedVariables() == {'C'}
    assert all(joined.getProbability(a) == 6 for a in joined.getAllPossibleAssignmentDicts())
    marginal = fo.eliminate(joined, 'B')
    assert all(marginal.getProbability(a) == 12 for a in marginal.getAllPossibleAssignmentDicts())
    assert marginal.variableDomainsDict() == domains
    # Impossible evidence is passed through the supplied normalize behavior.
    zero = bn.Factor(['A'], [], domains)
    net.setCPT('A', zero)
    assert inference.inferenceByVariableElimination(net, ['A'], {}, ['B']) is None
    print(f'[PASS] {comparisons} posterior/order comparisons; default orders; '
          'discard tracking; unnormalized factors; impossible evidence')


if __name__ == '__main__':
    check()
