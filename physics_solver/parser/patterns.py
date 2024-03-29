from spacy_pat_match_dsl.dsl import (
    PatternsGrammar,
    lower,
    Optional,
    lower_in,
    Or,
    And,
    lemma_in,
    lower_in_list,
    lemma_in_list,
    Token,
)

from sympy import Symbol

from physics_solver.math.variables import *
from physics_solver.util.functions import map_fst


unit_names_and_vars = [
    ("meter", Symbol("S")),
    ("centimeter", Symbol("S")),
    ("kilometer", Symbol("S")),
    ("hour", t),
    ("minute", t),
    ("second", t),
    ("gram", m),
    ("kilogram", m),
    ("candela", I),
    ("lux", E),
    ("revolution", N),
    ("hertz", nu),
    ("kilohertz", nu),
    ("tesla", B),
    ("megahertz", nu),
    ("gigahertz", nu),
    ("newton", F),
    ("kilonewton", F),
    ("joule", A),
    ("kilojoule", A),
    ("megajoule", A),
    ("ton", m),
]


compound_terms_and_vars = [
    ("ampere force", F),
    ("wave propagation", v),
    ("optical power", D),
    ("focal length", F),
    ("light intensity", I),
]


terms_and_vars = [
    ("density", ro),
    ("volume", V),
    ("degree", a),
    ("speed", v),
    ("length", l),
    ("moment", M),
    ("force", F),
    ("arm", d),
    ("wavelength", lam),
    ("power", P),
    ("pressure", p),
    ("capacitance", c),
    ("resistance", R),
    ("current", I),
    ("induction", B),
    ("illumination", E),
    ("height", h),
    ("period", T),
    ("frequency", nu),
    ("weight", P),
    ("mass", m),
    ("work", A),
    ("depth", h),
]


great_comparison_words = ["greater", "faster", "bigger", "larger", "longer"]
small_comparison_words = ["slower", "less", "smaller"]


class Patterns(PatternsGrammar):
    unit_name = lemma_in_list(map_fst(unit_names_and_vars))
    modifier = lower_in("cubic", "square")
    single_unit = Optional(modifier) + unit_name
    compound_unit = single_unit + lower("per") + single_unit
    UNIT = single_unit | compound_unit

    QUANTITY = Token({"LIKE_NUM": True}) + UNIT

    single_term = lower_in_list(map_fst(terms_and_vars))

    compound_term = Or(
        *[
            And(*[lower(w) for w in term.split()])
            for term in map_fst(compound_terms_and_vars)
        ]
    )

    simple_term = single_term | compound_term

    determiner = lower_in("a", "an", "the")

    of_term = simple_term + lower("of") + Optional(determiner) + simple_term

    TERM = simple_term | of_term

    UNKNOWN_QUESTION = lower_in("what", "determine", "calculate")

    positive_change_word = lemma_in("increase")
    negative_change_word = lemma_in("decrease", "reduce")
    change_pattern = (
        lower("by")
        + Optional(Optional(determiner) + lower("factor") + lower("of"))
        + Token({"LIKE_NUM": True})
    )
    POS_CHANGE = positive_change_word + change_pattern
    NEG_CHANGE = negative_change_word + change_pattern

    CHANGE_VERB = positive_change_word | negative_change_word | lower("change")

    special_unknown_word = lower_in("far", "fast", "often")
    UNKNOWN_HOW_QUESTION = lower("how") + special_unknown_word

    COMPARISON_WORD = lower_in_list(great_comparison_words) | lower_in_list(
        small_comparison_words
    )

    CONTEXT = lower_in(
        "converging", "diverging", "collecting", "square", "cube", "rectangle"
    )


print("\n".join(Patterns().to_bnf()))
