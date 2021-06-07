from subprocess import check_output

from TangentS.Tree_generator_tool import TreeCreator
from TangentS.math_tan.math_extractor import MathExtractor
from apted import APTED
from apted.helpers import Tree


def latex_math_to_slt_tuples(latex_formula):
    temp = MathExtractor.parse_from_tex(latex_formula)
    return temp.get_pairs(window=2, eob=True)


def latex_math_to_opt_tuples(latex_formula):
    temp = MathExtractor.parse_from_tex_opt(latex_formula)
    return temp.get_pairs(window=2, eob=True)


def latex_to_node(latex_str):
    slt = check_output(["latexmlmath", "--quiet", "--pmml=-", latex_str]).decode("utf-8")
    a = MathExtractor.convert_mathml_slt(slt)
    temp_lst_tuples = a.get_pairs(window=1, eob=True)
    lst_tuples = []
    for lst in temp_lst_tuples:
        line = lst.replace("}", "$$$")
        line = line.replace("{", "$$$")
        elements = line.split("\t")[0:3]
        lst_tuples.append(elements)
    return TreeCreator.direct_tuples_to_string(lst_tuples)


def math_ml_to_node(math_ml, is_slt, is_type, has_edge):
    if is_slt:
        a = MathExtractor.convert_mathml_slt(math_ml)
    else:
        a = MathExtractor.convert_mathml_opt(math_ml)

    temp_lst_tuples = a.get_pairs(window=1, eob=True)
    lst_tuples = []
    for lst in temp_lst_tuples:
        line = lst.replace("}", "$$$")
        line = line.replace("{", "$$$")
        elements = line.split("\t")[0:3]
        if is_type:
            for i in range(len(elements)):
                if "!" in elements[i] and elements[i] != "0!":
                    elements[i] = elements[i].split("!")[0]
        lst_tuples.append(elements)
    return TreeCreator.direct_tuples_to_string(lst_tuples, has_edge)


def math_ml_tuples(math_ml, is_slt):
    if is_slt:
        a = MathExtractor.convert_mathml_slt(math_ml)
    else:
        a = MathExtractor.convert_mathml_opt(math_ml)

    temp_lst_tuples = a.get_pairs(window=1, eob=True)
    return temp_lst_tuples


def math_ml_to_node2(math_ml, is_slt):
    if is_slt:
        a = MathExtractor.convert_mathml_slt(math_ml)
    else:
        a = MathExtractor.convert_mathml_opt(math_ml)

    temp_lst_tuples = a.get_pairs(window=1, eob=True)
    lst_tuples = []
    for lst in temp_lst_tuples:
        line = lst.replace("}", "$$$")
        line = line.replace("{", "$$$")
        elements = line.split("\t")[0:4]
        # print(elements)
        # input("check")
        lst_tuples.append(elements)
    depth = TreeCreator.get_tree_depth(lst_tuples)
    variation = TreeCreator.get_variation_from_baseline(lst_tuples)
    root = TreeCreator.direct_tuples_to_string(lst_tuples, False)
    return root, depth, variation


def get_tree_distance(node_1, node_2):
    tree1, tree2 = map(Tree.from_text, [node_1, node_2])
    apted = APTED(tree1, tree2)
    return apted.compute_edit_distance()


def get_slt_string(slt):
    a = MathExtractor.convert_mathml_slt(slt)
    return a.tostring()


def harmonic_prec_recall(math_ml1, math_ml2, is_slt, is_type):
    if is_slt:
        a = MathExtractor.convert_mathml_slt(math_ml1)
        b = MathExtractor.convert_mathml_slt(math_ml2)
    else:
        a = MathExtractor.convert_mathml_opt(math_ml1)
        b = MathExtractor.convert_mathml_opt(math_ml2)

    lst_tuples1 = a.get_pairs(window=2, eob=True)
    lst_tuples2 = b.get_pairs(window=2, eob=True)
    lst_tuples_f = []
    for lst in lst_tuples1:
        elements = lst.split("\t")[0:4]
        if is_type:
            for i in range(len(elements)):
                if "!" in elements[i] and elements[i] != "0!":
                    elements[i] = elements[i].split("!")[0]
        lst_tuples_f.append(''.join(elements))
    lst_tuples_s = []
    for lst in lst_tuples2:
        elements = lst.split("\t")[0:4]
        if is_type:
            for i in range(len(elements)):
                if "!" in elements[i] and elements[i] != "0!":
                    elements[i] = elements[i].split("!")[0]
        lst_tuples_s.append(''.join(elements))

    found = 0.0
    for item in lst_tuples_s:
        if item in lst_tuples_f:
            found += 1

    recall = found / len(lst_tuples_s)
    precision = found / len(lst_tuples_f)
    harmonic_mean = (2*recall*precision) / (recall+precision+1)
    return harmonic_mean
