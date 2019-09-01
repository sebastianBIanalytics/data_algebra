
import pandas         # https://pandas.pydata.org
import yaml           # https://pyyaml.org
from data_algebra.data_ops import *  # https://github.com/WinVector/data_algebra
import data_algebra.env
import data_algebra.yaml
import data_algebra.PostgreSQL
import data_algebra.util

def test_scoring_example():
    # set some things in our environment
    data_algebra.env.push_onto_namespace_stack(locals())
    # ask YAML to write simpler structures
    data_algebra.yaml.fix_ordered_dict_yaml_rep()

    d_local = pandas.DataFrame({
        'subjectID': [1, 1, 2, 2],
        'surveyCategory': ["withdrawal behavior", "positive re-framing", "withdrawal behavior", "positive re-framing"],
        'assessmentTotal': [5, 2, 3, 4],
        'irrelevantCol1': ['irrel1'] * 4,
        'irrelevantCol2': ['irrel2'] * 4,
    })

    db_model = data_algebra.PostgreSQL.PostgreSQLModel()

    scale = 0.237

    with data_algebra.env.Env(locals()) as env:
        ops = TableDescription('d',
                               ['subjectID',
                                'surveyCategory',
                                'assessmentTotal',
                                'irrelevantCol1',
                                'irrelevantCol2']). \
            extend({'probability': '(assessmentTotal * scale).exp()'}). \
            extend({'total': 'probability.sum()'},
                   partition_by='subjectID'). \
            extend({'probability': 'probability/total'}). \
            extend({'row_number': '_row_number()'},
                   partition_by=['subjectID'],
                   order_by=['probability', 'surveyCategory'],
                   reverse=['probability']). \
            select_rows('row_number==1'). \
            select_columns(['subjectID', 'surveyCategory', 'probability']). \
            rename_columns({'diagnosis': 'surveyCategory'}). \
            order_rows(['subjectID'])

    data_algebra.yaml.check_op_round_trip(ops)

    py_source = ops.to_python(strict=True, pretty=False)
    py_sourcep = ops.to_python(strict=True, pretty=True)

    sql = ops.to_sql(db_model, pretty=True)

    # Pandas calculate
    res = ops.eval_pandas({'d': d_local})
    expect = pandas.DataFrame({
        'subjectID': [1, 2],
        'diagnosis': ['withdrawal behavior', 'positive re-framing'],
        'probability': [0.670622, 0.558974]
    })
    assert data_algebra.util.equivalent_frames(expect, res, float_tol=1e-3)

    # round-trip the operators
    objs_Python = ops.collect_representation()
    dmp_Python = yaml.dump(objs_Python)
    ops_back = data_algebra.yaml.to_pipeline(yaml.safe_load(dmp_Python))
    assert isinstance(ops_back, data_algebra.data_ops.ViewRepresentation)

    py_sourceb = ops_back.to_python(strict=True, pretty=False)
    assert py_source == py_sourceb
