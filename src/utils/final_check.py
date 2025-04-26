def validate_answer(answer, context=None):
    """
    Valide la réponse fournie en fonction de critères spécifiques.

    Cette fonction vérifie si la réponse est une chaîne non vide qui se termine par le préfixe "FINAL ANSWER: ".
    Elle valide ensuite la partie réponse finale pour s'assurer qu'elle est soit un chiffre, soit une liste de chiffres séparés par des virgules,
    soit une liste de chaînes alphabétiques séparées par des virgules.
    Args:
        answer (str): La réponse à valider.
        context (any): Contexte supplémentaire (facultatif).
    Returns:
        tuple: Un tuple contenant un booléen et une chaîne. Le booléen indique si la réponse est valide,
               et la chaîne fournit un message décrivant le résultat de la validation.
    """
    if not answer:                                      # Vérifie si la réponse est vide
        return False, "La réponse est vide."

    if not isinstance(answer, str):                     # Vérifie si la réponse est une chaîne
        return False, "La réponse doit être une chaîne."

    final_answer_prefix = "FINAL ANSWER: "                              # Définit le préfixe attendu pour la réponse finale
    if not answer.strip().endswith(final_answer_prefix):                # Vérifie si la réponse se termine par "FINAL ANSWER: "
        return False, "La réponse doit se terminer par 'FINAL ANSWER: '."

    final_answer_part = answer[:-len(final_answer_prefix)].strip()      # Extrait la partie réponse finale

    if not final_answer_part:                                   # Vérifie si la réponse finale est vide
        return False, "La réponse finale est vide."

    if final_answer_part.isdigit():                         # Vérifie si la réponse finale est un nombre
        return True, "La réponse est valide."

    parts = final_answer_part.split(',')          # Vérifie s'il s'agit d'une liste séparée par des virgules
    for part in parts:
        part = part.strip()
        if part.isdigit() or (part.replace('.', '', 1).isdigit()):          # Vérifie si chaque élément est un nombre
            continue
        if not part.replace(' ', '').isalpha():                 # Vérifie si chaque élément est une chaîne alphabétique
            return False, "La réponse contient des éléments invalides."

    return True, "La réponse est valide."                 # Retourne vrai si toutes les vérifications sont passées
