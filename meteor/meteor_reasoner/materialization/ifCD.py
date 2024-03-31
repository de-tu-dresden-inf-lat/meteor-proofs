CD = ["<","<=","=","!=",">",">="]
# CD predicates have the following shape: #[1,5,=,5](S,D) to denote a linear equation 1 * S + 5 * D = 5
# for "=" and "!=" is it allowed to compare also non-numbers -- then the syntax must be #[!=](X,Y,Z)

def isCD(predicate):
    if predicate[0]=="#":
        return True
    else:
        return False

def ifCD(predicate,entity):
    #mostly for numbers, but != and = also for constants
    # check the syntax
    #print(predicate)
    if (predicate[0]!="#") or (predicate[1]!="[") or (predicate[-1]!="]"):
        print("Error: the CD operator " + predicate + " does not follow the syntax #[...]")
        return False
    else:
        tr_predicate = predicate[2:-1].split(',')
        #print(tr_predicate)
        if len(tr_predicate) == 1: #comparing non-numbers
            if tr_predicate[0] not in ["=","!="] or (len(entity) < 2):
                print("Error: the CD operator " + predicate + " does not follow the syntax. Only = and != between two+ obj are allowed as singletons")
                return False
            else:
                if tr_predicate[0] == "=":
                    for i in entity:
                        if i.name != entity[0].name:
                            return False
                    return True
                else: #((tr_predicate[0] == "!=")
                    for i in range(len(entity)):
                        for j in range(len(entity)):
                            if (i != j) and (entity[i].name == entity[j].name):
                                return False
                    return True
        elif len(tr_predicate) < 3: #too short
            print("Error: the CD operator " + predicate + " does not follow the syntax. Impossible to break the string")
            return False
        else: #below should be all numbers
            cd_operator = tr_predicate[-2]
            str_coefficients = tr_predicate[:-2]
            str_right_side = tr_predicate[-1]
            if cd_operator not in CD:
                print("Error: the CD operator " + cd_operator + " is unknown")
                return False
        #convert the numbers
            cd_coefficients = []
            try:
                cd_right_side = int(str_right_side)
                for i in str_coefficients:
                    cd_coefficients.append(int(i))
            except:
                print("Error: in the brackets of " + predicate + " there must be numbers")
                return False
            num = []
            try:
                for i in entity:
                    num.append(int(i.name))
            except:
                print("Constants " + entity[0].name + ", " + entity[1].name + " must be  numbers")
                return False
        #check the cardinality
            if len(num) != len(cd_coefficients):
                print("Cardinality of the operator " + predicate + " does not match with given " + str(len(entity)) + " inputs")
                return False

            cd_left_side = 0
            for i in range(len(num)):
                cd_left_side += num[i]*cd_coefficients[i]
            
        # check the validity
            if cd_left_side == cd_right_side:
                if cd_operator in ["=","<=",">="]:
                    return True
                else:
                    return False
            elif cd_left_side < cd_right_side:
                if cd_operator in ["<","<=","!="]:
                    return True
                else:
                    return False
            else:
                if cd_operator in [">",">=","!="]:
                    return True
                else:
                    return False
