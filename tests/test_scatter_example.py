
import pandas

import data_algebra.util
import data_algebra.cdata
import data_algebra.cdata_impl

# https://github.com/WinVector/cdata

def test_scatter_example():
    meas_vars = ['Sepal.Length', 'Sepal.Width', 'Petal.Length', 'Petal.Width']
    pairs = [(a, b) for a in meas_vars for b in meas_vars]
    control_table = pandas.DataFrame({
        'v1': [p[0] for p in pairs],
        'v2': [p[1] for p in pairs],
    })
    control_table['value_1'] = control_table['v1']
    control_table['value_2'] = control_table['v2']
    record_map = data_algebra.cdata_impl.RecordMap(
        blocks_out=data_algebra.cdata.RecordSpecification(
            control_table,
            record_keys=['iris_id', 'Species'],
            control_table_keys=['v1', 'v2']
        )
    )

    str = format(record_map)
    iris_small = pandas.DataFrame({
        'iris_id': [1, 100],
        'Sepal.Length': [5.1, 5.7],
        'Sepal.Width': [3.5, 2.8],
        'Petal.Length': [1.4, 4.1],
        'Petal.Width': [0.2, 1.3],
        'Species': ['setosa', 'versicolor'],
    })
    res = record_map.transform(iris_small)
    expect = pandas.DataFrame({
        'iris_id': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100],
        'Species': ['setosa', 'setosa', 'setosa', 'setosa', 'setosa', 'setosa', 'setosa', 'setosa', 'setosa', 'setosa', 'setosa', 'setosa', 'setosa', 'setosa', 'setosa', 'setosa', 'versicolor', 'versicolor', 'versicolor', 'versicolor', 'versicolor', 'versicolor', 'versicolor', 'versicolor', 'versicolor', 'versicolor', 'versicolor', 'versicolor', 'versicolor', 'versicolor', 'versicolor', 'versicolor'],
        'v1': ['Petal.Length', 'Petal.Length', 'Petal.Length', 'Petal.Length', 'Petal.Width', 'Petal.Width', 'Petal.Width', 'Petal.Width', 'Sepal.Length', 'Sepal.Length', 'Sepal.Length', 'Sepal.Length', 'Sepal.Width', 'Sepal.Width', 'Sepal.Width', 'Sepal.Width', 'Petal.Length', 'Petal.Length', 'Petal.Length', 'Petal.Length', 'Petal.Width', 'Petal.Width', 'Petal.Width', 'Petal.Width', 'Sepal.Length', 'Sepal.Length', 'Sepal.Length', 'Sepal.Length', 'Sepal.Width', 'Sepal.Width', 'Sepal.Width', 'Sepal.Width'],
        'v2': ['Petal.Length', 'Petal.Width', 'Sepal.Length', 'Sepal.Width', 'Petal.Length', 'Petal.Width', 'Sepal.Length', 'Sepal.Width', 'Petal.Length', 'Petal.Width', 'Sepal.Length', 'Sepal.Width', 'Petal.Length', 'Petal.Width', 'Sepal.Length', 'Sepal.Width', 'Petal.Length', 'Petal.Width', 'Sepal.Length', 'Sepal.Width', 'Petal.Length', 'Petal.Width', 'Sepal.Length', 'Sepal.Width', 'Petal.Length', 'Petal.Width', 'Sepal.Length', 'Sepal.Width', 'Petal.Length', 'Petal.Width', 'Sepal.Length', 'Sepal.Width'],
        'value_1': [1.4, 1.4, 1.4, 1.4, 0.2, 0.2, 0.2, 0.2, 5.1, 5.1, 5.1, 5.1, 3.5, 3.5, 3.5, 3.5, 4.1, 4.1, 4.1, 4.1, 1.3, 1.3, 1.3, 1.3, 5.7, 5.7, 5.7, 5.7, 2.8, 2.8, 2.8, 2.8],
        'value_2': [1.4, 0.2, 5.1, 3.5, 1.4, 0.2, 5.1, 3.5, 1.4, 0.2, 5.1, 3.5, 1.4, 0.2, 5.1, 3.5, 4.1, 1.3, 5.7, 2.8, 4.1, 1.3, 5.7, 2.8, 4.1, 1.3, 5.7, 2.8, 4.1, 1.3, 5.7, 2.8],
        })
    assert data_algebra.util.equivalent_frames(res, expect)

    inv = record_map.inverse()
    back = inv.transform(expect)
    assert data_algebra.util.equivalent_frames(iris_small, back)
