from enum import Enum
from typing import Set
from server import Listener, ProficiencyLevel

class FilterMode(Enum):
    AND = "AND"
    OR = "OR"

# TODO: This is a naive implementation; see if this can be made more efficient
def filter_listeners(
    language_requirements: dict[str, ProficiencyLevel],
    mode: FilterMode = FilterMode.AND
) -> Set[str]:
    """
    Filters all listeners based on proficiency in the specified languages.

    Args:
        language_requirements: The languages the users are required to know along with the required proficiency.
        mode: Whether to ensure that at least one requirement is fulfilled (OR) or all of them (AND).

    Returns:
        A set of UUIDs of users who meet the requirements.
    """
    # Define a lambda to encapsulate the filter condition
    meets_proficiency = lambda lang, proficiency: ProficiencyLevel.from_str(
        Listener.languages[lang].astext
    ) >= proficiency.value

    query = Listener.query

    if mode == FilterMode.AND:
        # Chain the filters for all language-proficiency pairs
        for lang, proficiency in language_requirements.items():
            query = query.filter(meets_proficiency(lang, proficiency))
        filtered_users = set(query(Listener.id))
    else:
        # Accumulate results for each condition to cover the OR mode
        filtered_users = set()
        for lang, proficiency in language_requirements.items():
            filtered_users.update(query(Listener.id).filter(meets_proficiency(lang, proficiency)))
            
    return filtered_users
