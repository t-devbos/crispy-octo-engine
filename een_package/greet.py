print(f"__name__ van de module greet is nu: {__name__}")


def greet (naam: str = "everyone") -> str:
    return f"greetings {naam}"

def salutations (naam: str = "all") -> str:
    return f"salutations {naam}"

if __name__ == "__main__":
    print(greet())
    print(salutations)