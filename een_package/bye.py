print(f"__name__ van de module bye is nu: {__name__}")


def bye (naam: str = "world") -> str:
    return f"bye {naam}"

def goodnight (naam: str = "everyone") -> str:
    return f"goodnight {naam}"

if __name__ == "__main__":
    print(bye())
    print(goodnight())