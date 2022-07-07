from apps.api.models import UGSNames


def load_ugs() -> list:
    UGS_names_list = []

    for name in UGSNames.objects.all():
        UGS_names_list.append(name.name)

    return UGS_names_list
