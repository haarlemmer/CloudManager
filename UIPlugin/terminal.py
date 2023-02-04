class UIInstance:
    def __init__(self) -> None:
        pass

    # Simple UI
    def title(self,title:str) -> None:
        print(f"----------{title}----------")
    def yesno(self,question):
        choice = input(f"{question} [Y/N]")
        if choice == "Yes" or choice == "yes" or choice == "Y" or choice == "y":
            output = True
        else:
            output = False
        return output
    def message(self,message):
        print(message)
    def textInput(self,prompt):
        return input(prompt)

    # UI For Instance Management
    def listSelect(self,list:list,title:str,info:str) -> str:
        self.title(title)
        print(info)
        for x in range(len(list)):
            print(f"{x+1}. {list[x]}")
        return input("Select: ")
    def actionOverview(self,action: str,instance: str,options: str) -> bool:
        self.title("Action Overview")
        print(f"Instance: {instance}")
        print(f"Action: {action}")
        print(f"Options: {options}")
        confirm = self.yesno("Confirm?")
        if confirm:
            return True
        return False
    def options(self,title:str,options:list) -> list:
        self.title(title)
        answer = []
        for option in options:
            if option['type'] == 'yesno':
                answer.append(self.yesno(option['question']))
            if option['type'] == 'text':
                print(option['question'])
                answer.append(input("> "))
        return answer

