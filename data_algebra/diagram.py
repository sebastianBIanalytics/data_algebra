
have_graphviz = False
try:
    # noinspection PyUnresolvedReferences
    import graphviz

    have_graphviz = True
except ImportError:
    have_graphviz = False

import data_algebra.data_ops


def _to_digraph_r_nodes(ops, dot, table_keys, nextid, edges):
    if isinstance(ops, data_algebra.data_ops.TableDescription):
        if ops.key in table_keys:
            return table_keys[ops.key]
        table_keys.add(ops.key)
        node_id = nextid[0]
        nextid[0] = node_id + 1
        dot.attr('node', shape="folder", color='blue')
        dot.node(str(node_id), ops.to_python_implementation(print_sources=False))
        return node_id
    source_ids = [_to_digraph_r_nodes(ops=op,
                                      dot=dot,
                                      table_keys=table_keys,
                                      nextid=nextid, edges=edges) for op in ops.sources]
    node_id = nextid[0]
    nextid[0] = node_id + 1
    if len(source_ids) > 1:
        for i in range(len(source_ids)):
            sub_id = source_ids[i]
            edges.append((str(sub_id), str(node_id), "_" + str(i)))
    else:
        for sub_id in source_ids:
            edges.append((str(sub_id), str(node_id), None))
    dot.attr('node', shape='note', color='darkgreen')
    dot.node(str(node_id), ops.to_python_implementation(print_sources=False))
    return node_id


def to_digraph(ops):
    if not have_graphviz:
        raise RuntimeError("graphviz not installed")
    dot = graphviz.Digraph()
    edges = []
    _to_digraph_r_nodes(ops=ops, dot=dot, table_keys=set(), nextid=[0], edges=edges)
    for (sub_id, node_id, label) in edges:
        if label is None:
            dot.edge(sub_id, node_id)
        else:
            dot.edge(sub_id, node_id, label=label)
    return dot