import re
import collections

import pandas

import data_algebra.data_types



def table_is_keyed_by_columns(table, column_names):
    # check for ill-condition
    missing_columns = set(column_names) - set([c for c in table.columns])
    if len(missing_columns) > 0:
        raise KeyError("missing columns: " + str(missing_columns))
    # get rid of some corner cases
    if table.shape[0] < 2:
        return True
    if len(column_names) < 1:
        return False
    ops = (
        data_algebra.data_ops.describe_table(table, "table")
        .select_columns(column_names)
        .extend({"cdata_temp_one": 1})
        .project({"_cdata_temp_sum": "cdata_temp_one.sum()"}, group_by=column_names)
        .project({"_cdata_temp_sum": "_cdata_temp_sum.max()"})
    )
    t2s = ops.transform(table)
    return t2s.iloc[0, 0] <= 1


class RecordSpecification:
    def __init__(self, control_table, *,
                 record_keys=None, control_table_keys=None, strict=False):
        control_table = data_algebra.data_types.convert_to_pandas_dataframe(
            control_table, "control_table"
        )
        control_table = control_table.reset_index(inplace=False, drop=True)
        if control_table.shape[0] < 2:
            raise ValueError("control table should have at least 2 rows")
        self.control_table = control_table.reset_index(drop=True)
        if record_keys is None:
            record_keys = []
        if not isinstance(record_keys, list):
            record_keys = [record_keys]
        self.record_keys = [k for k in record_keys]
        if control_table_keys is None:
            control_table_keys = [control_table.columns[0]]
        if not isinstance(control_table_keys, list):
            record_keys = [control_table_keys]
        self.control_table_keys = [k for k in control_table_keys]
        if len(self.control_table_keys) < 1:
            raise ValueError("control table should have at least one key column")
        unknown =  set(self.control_table_keys) - set(control_table.columns)
        if len(unknown) > 0:
            raise ValueError("control table keys that are not in the control table: " + str(unknown))
        if len(self.control_table_keys) >= control_table.shape[1]:
            raise ValueError("control table should have at least one non-key column")
        confused = set(record_keys).intersection(control_table_keys)
        if len(confused) > 0:
            raise ValueError(
                "columns common to record_keys and control_table_keys: " + str(confused)
            )
        if strict:
            if not table_is_keyed_by_columns(self.control_table, self.control_table_keys):
                raise ValueError("control table wasn't keyed by control table keys")
        self.block_columns = self.record_keys + [c for c in self.control_table.columns]
        cvs = []
        for c in self.control_table:
            if not c in self.control_table_keys:
                for v in self.control_table[c]:
                    if not v in cvs:
                        cvs.append(v)
        confused = set(record_keys).intersection(cvs)
        if len(confused) > 0:
            raise ValueError(
                "control table entries confused with row keys or control table keys"
            )
        self.row_columns = self.record_keys + cvs

    def row_version(self, *, include_record_keys=True):
        cols = []
        if include_record_keys:
            cols = cols + self.record_keys
        for ci in self.control_table.columns:
            if ci not in self.control_table_keys:
                for c in self.control_table[ci]:
                    cols.append(c)
        return cols

    def fmt(self):
        s = (
            "RecordSpecification\n"
            + "   record_keys: "
            + str(self.record_keys)
            + "\n"
            + "   control_table_keys: "
            + str(self.control_table_keys)
            + "\n"
            + "   control_table:\n"
            + "   "
            + re.sub("\n", "\n   ", str(self.control_table))
            + "\n"
        )
        return s

    def __repr__(self):
        return self.fmt()

    def __str__(self):
        return self.fmt()

    def to_simple_obj(self):
        """Create an object for YAML encoding"""

        obj = collections.OrderedDict()
        obj["type"] = "data_algebra.cdata.RecordSpecification"
        obj["record_keys"] = self.record_keys.copy()
        obj["control_table_keys"] = self.control_table_keys.copy()
        tbl = collections.OrderedDict()
        for k in self.control_table.columns:
            tbl[k] = [v for v in self.control_table[k]]
        obj["control_table"] = tbl
        return obj


def record_spec_from_simple_obj(obj):
    control_table = pandas.DataFrame()
    for k in obj["control_table"].keys():
        control_table[k] = obj["control_table"][k]

    def maybe_get_list(map, key):
        try:
            v = map[key]
            if v is None:
                return []
            if not isinstance(v, list):
                v = [v]
            return v
        except KeyError:
            return []

    return RecordSpecification(
        control_table,
        record_keys=maybe_get_list(obj, "record_keys"),
        control_table_keys=maybe_get_list(obj, "control_table_keys"),
    )
