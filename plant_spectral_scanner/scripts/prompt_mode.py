def prompt_mode() -> str:
    """
    Prompt the user to select scan, baseline, or quit mode
    """
    while True:
        print("\nSelect mode:")
        print("[1] Scan")
        print("[2] Baseline")
        print("[3] Quit")
        choice = input("Enter 1, 2 or 3: ").strip()
        if choice == '1':
            return "scan"
        elif choice == '2':
            return "baseline"
        elif choice == '3':
            return "quit"
        else:
            print("Invalid input. Please enter 1, 2 or 3.")
