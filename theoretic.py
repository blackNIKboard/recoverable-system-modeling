def calculate_upper_bound(schema, upper_bound_lamb, upper_bound_lamb_mu):
    readiness_coefficient = upper_bound_lamb_mu / (upper_bound_lamb + upper_bound_lamb_mu)
    upper_bound = 1

    for part in schema:
        if isinstance(part, int):
            upper_bound *= readiness_coefficient
        elif isinstance(part, list):
            for subpart in part:
                if not isinstance(subpart, int):
                    raise ValueError('invalid type in state {}'.format(type(subpart)))
            upper_bound *= (1 - (1 - readiness_coefficient) ** len(part))
        else:
            raise ValueError('invalid type in state {}'.format(type(part)))

    return upper_bound


def calculate_lower_bound(schema, lower_bound_lamb, lower_bound_lamb_mu):
    readiness_coefficient = lower_bound_lamb_mu / (lower_bound_lamb + lower_bound_lamb_mu)
    result = 1

    for _ in schema:
        result *= readiness_coefficient

    return result
