import bs_types
import time
import UPL

## change most calls to self.MEMORY.env to self.MEMORY.blue_memory_get() - ryan 03:19
class BS_BUILTIN:
    def __init__(self, MEMORY, errorHandler):
        self.MEMORY = MEMORY  ## memory ref
        self.ErrorHandler = errorHandler ## handles all of the errors

    def blue_varUpdate(self, args):
        ## mode = 0 numbers
        ## mode = 1 string
        mutable = True ## can something be mutable?
        mode = 0
        
        if '=' in args:
            var, data = args.split('=',1)

            ## cleanup data
            var = var.rstrip()
            data = data.lstrip()

            ## check if we are adding anything
            check = any(map(args.__contains__, bs_types.MATH_ARRAY))  
            varname = var
            var = self.MEMORY.var_get(varname)
            
            if var == False:
                raise Exception(f"'{varname}' does not exist.")

            if var[2] == False:
                raise Exception(f"Cannot change unmutable value.")

            ## fixed minor issue (data was chaning the type, and mutable became the data)
            if not check:
                temp = self.MEMORY.var_get(data)

                if temp == False:
                    data = self.MEMORY.type_guess(data)
                else:
                    data = temp[1]

                self.MEMORY.var_add(varname,var[0] ,data, mutable)
                return

            ## clean up later
            if self.MEMORY.var_get(varname) != False: ## exists

                ## math stuff
                math_oper = next(substring for substring in bs_types.MATH_ARRAY if substring in data)
                item_1, item_2 = data.split(math_oper, 1)
                math_oper = "**" if math_oper == "^" else math_oper
                
                ## remove leading/trailing useless spaces
                item_1 = item_1.rstrip()
                item_2 = item_2.lstrip()
                ## get variable data
                temp1 = self.MEMORY.var_get(item_1)
                temp2 = self.MEMORY.var_get(item_2)

                if temp1 == False:
                    item_1 = self.MEMORY.type_guess(item_1)

                else:
                    item_1 = temp1[1]

                if temp2 == False:
                    item_2 = self.MEMORY.type_guess(item_2)
                
                else:
                    item_2 = temp2[1]

                ## if string make string
                if type(item_1) == str and '\"' not in item_1: item_1 = f'\"{item_1}\"'; mode = 1
                if type(item_2) == str and '\"' not in item_2: item_2 = f'\"{item_2}\"'; mode = 1

                eval_string = f"{item_1} {math_oper} {item_2}"
                ## string stuff
                if mode == 1:
                    self.MEMORY.var_add(varname, var[0], f"\"{eval(eval_string)}\"", mutable)
                    return

                
                self.MEMORY.var_add(varname, var[0], eval(eval_string), mutable)
                return
            
            raise Exception(f"Variable '{varname}' does not exist")

        raise Exception("No value being set.")

    def blue_typeof(self, args):
        lookAt, returnVar = args.split(bs_types.TO_CHAR, 1)
        
        ## string cleanup
        lookAt = lookAt.rstrip()
        returnVar = returnVar.lstrip()
        
        lookatVar = self.MEMORY.var_get(lookAt)
        returnVarData = self.MEMORY.var_get(returnVar)
        
        if returnVarData == False:
            raise Exception(f"Unknown output variable '{returnVar}'")
        
        if lookatVar != False:
            if returnVarData[2] == False:
                raise Exception(f"You are not allowed to change unmutable variable '{returnVar}'")
            self.MEMORY.var_add(returnVar, returnVarData[0], lookatVar[0], returnVarData[4])        
            return
        
        raise Exception(f"'{lookAt}' does not exist")
        
    def blue_input(self, args):
        tmp = "" ## for output stuff
        prompt, output = args.split(bs_types.TO_CHAR, 1)
        ## clean up prompt
        prompt = prompt.rstrip()
        if '"' in prompt: prompt = prompt.replace('"','')

        ## clean up output
        output = output.lstrip()

        temp = self.MEMORY.var_get(prompt)
        out = self.MEMORY.var_get(output)

        if out == False:
            pass

        if temp == False:
            tmp = input(prompt)

        else:
            tmp = input(temp[1])

        if out[0] == 'str':
            tmp = f"\"{tmp}\""

        output_string = f'{output} = {tmp}'

        self.blue_varUpdate(output_string)
        

    def call_func(self, args):
        output = None
        func_name, args = args.split("(", 1)
        args = args.replace(')', '') ## remove tailing
        args = args.replace(' ', '')
        
        if bs_types.TO_CHAR in args:
            args, output = args.split(bs_types.TO_CHAR, 1)
            
            if self.MEMORY.var_get(output) == False:
                raise Exception(f"Unknown var '{output}'")
            
            if ',' in args:
                func_args = args.split(',')
                #print(func_name)
                needed_args = self.MEMORY.env["functions"][func_name]["args"]
                for x in range(len(needed_args)):
                    arg_get = self.MEMORY.var_get(func_args[x])
                        
                    if arg_get == False:
                        data = self.MEMORY.type_guess(func_args[x])
                        dtype = ""
                        if type(data) == str    : dtype = "str"
                        elif type(data) == int  : dtype = "int"
                        elif type(data) == float: dtype = "float"
                        elif type(data) == bool : dtype = "bool"
                        self.MEMORY.set_scope(func_name)
                        self.MEMORY.var_add(needed_args[x], dtype, data, True)

                    else:
                        self.MEMORY.set_scope(func_name)
                        self.MEMORY.var_add(needed_args[x], arg_get[0], arg_get[1], arg_get[2])

                    self.MEMORY.back_scope()
                    
        args = UPL.Core.removeEmpty(args.split(','))
        if func_name in list(self.MEMORY.env["functions"].keys()):
            func_data = self.MEMORY.env['functions'][func_name]
            
            needed_args = self.MEMORY.env["functions"][func_name]["args"]
            for x in range(len(needed_args)):
                arg_get = self.MEMORY.var_get(args[x])
                        
                if arg_get == False:
                    data = self.MEMORY.type_guess(args[x])
                    dtype = ""
                    if type(data) == str    : dtype = "str"
                    elif type(data) == int  : dtype = "int"
                    elif type(data) == float: dtype = "float"
                    elif type(data) == bool : dtype = "bool"
                    self.MEMORY.set_scope(func_name)
                    self.MEMORY.var_add(needed_args[x], dtype, data, True)

                else:
                    self.MEMORY.set_scope(func_name)
                    self.MEMORY.var_add(needed_args[x], arg_get[0], arg_get[1], arg_get[2])

                self.MEMORY.back_scope()
                    
                
            
            if len(args) != len(func_data['args']):
                raise Exception(f"'{func_name}' expected {len(func_data['args'])} but got {len(args)}")
            
            code = func_data['code']
            
            return ('func_code', code, output, func_name)

        raise Exception(f"{func_name} has not been defined")
            
    def blue_mem_free(self, args):
        args = args.lstrip().rstrip()
        temp = self.MEMORY.var_get(args)
        
        if temp == False:
            return

        del self.MEMORY.env["vars"][self.MEMORY.current_scope][args]
        

    def blue_logicalIf(self, args):
        ## check if args contains a logic operator
        check = any(map(args.__contains__, bs_types.LOGIC_ARRAY))    

        if check == True:  
            ## get the logic operator 
            logic_operator = next(substring for substring in bs_types.LOGIC_ARRAY if substring in args)
            ## get items to check
            item_1, item_2 = args.split(logic_operator, 1)

            ## remove leading/trailing useless spaces
            item_1 = item_1.rstrip()
            item_2 = item_2.lstrip()

            temp1 = self.MEMORY.var_get(item_1)
            temp2 = self.MEMORY.var_get(item_2)

            if temp1 == False:
                item_1 = self.MEMORY.type_guess(item_1)

            else:
                if temp1[0] == 'str':
                    if '\"' not in temp1[1]:
                        item_1 = f'"{temp1[1]}"'
                    else:
                        item_1 = temp1[1]
                else:
                    item_1 = temp1[1]

            if temp2 == False:
                item_2 = self.MEMORY.type_guess(item_2)
            
            else:
                if temp2[0] == 'str':
                    if '\"' not in temp2[1]:
                        item_2 = f'"{temp2[1]}"'
                else:
                    item_2 = temp2[1]


            eval_string = f"{item_1} {logic_operator} {item_2}"
            #print(eval_string)
            return ("LOGIC_OUT",eval(eval_string))

    def blue_goif(self, args):
        args, goto_loc = args.split(bs_types.TO_CHAR, 1)
        goto_loc =  goto_loc.lstrip() ## clean up string
        goto_data = self.MEMORY.lable_get(goto_loc.lstrip())

        if goto_data == "NULL":
            raise Exception(f"'{goto_loc}' does not exist")

        out = self.blue_logicalIf(args.rstrip()) ## send with removing trailing spaces
        
        if out[1] == False:
            return ("goto_out", False)
        return ("lable_location", goto_data)

    def blue_lable(self, args):
        self.MEMORY.lable_add(args, self.MEMORY.CurrentLine)

    def blue_goto(self, args):
        lable_data = self.MEMORY.lable_get(args)
        
        if lable_data == "NULL":
            raise Exception(f"Lable '{args}' does not exist")

        return ('lable_location',lable_data)

    def blue_vardec(self, args):
        mutable = True
        is_global = False
        if 'const' in args:
            mutable = False
            args = args.replace("const", '').lstrip().rstrip()
        
        if "glob" in args:
            is_global = True
            args = args.replace("glob", '').lstrip().rstrip()
            
        dtype, args = args.split(' ', 1) ## get type and args
        
        if '=' in args:
            name, data = args.split('=', 1)
            name = name.rstrip() ## remove tailing spaces
            data = data.lstrip() ## remove leading spaces
            out = self.MEMORY.var_get(data)

            ## not var
            if out != False:
                self.MEMORY.var_add(name, dtype, out, mutable, is_global)
            
            ## var
            else:
                self.MEMORY.var_add(name, dtype, data, mutable, is_global)

        else:
            self.MEMORY.var_add(args, dtype, bs_types.null, mutable, is_global)


    ## append to blue arrays
    def blue_append(self, args):
        ## append 'data' -> array
        data, varname = args.split(bs_types.TO_CHAR, 1)
        
             
        data = data.rstrip()
        varname = varname.lstrip()
        main_var = self.MEMORY.var_get(varname)
                
        if main_var == False:
            raise Exception(f"Variable '{main_var}' does not exist")

        if main_var[0] != 'array':
            raise TypeError(f"Cannot append to type '{main_var[0]}'")
        
        var_data = main_var[1]
        
        temp_var = self.MEMORY.var_get(data)
        
        if temp_var == False:
            data = self.MEMORY.type_guess(data)
        else:
            ## 2nd index of variables are data
            data = temp_var[1]
        
        if type(data) == str and '"' in data:
            data = data.replace('"','')
        var_data.append(data)    
        
        self.MEMORY.var_add(varname, "array", var_data, True, False)
        
    def blue_sizeof(self, args):
        if bs_types.TO_CHAR in args:
            var1, var2 = args.split(bs_types.TO_CHAR)
            var1 = var1.rstrip()
            var2 = var2.lstrip()
            
            var_data1 = self.MEMORY.var_get(var1)
            output = self.MEMORY.var_get(var2)
            if output == False or output[0] != "int":
                raise Exception(f"'{output}' does not exist or is incorrect type")
            
            if var_data1 == False:
                var_data1 = len(self.MEMORY.type_guess(var1))
            else:
                var_data1 = len(var_data1[1])
        
            self.MEMORY.var_add(var2,"int",var_data1,output[2])
            return
        
        raise Exception("Expected '->' but could not find it.")

    ## create blue array
    def blue_array(self, args):

        ## has '='
        if '=' in args:
            name, data = args.split('=')
            
            ## clean string
            name = name.rstrip()
            data = data.lstrip().replace('[','').replace(']','')

            if ',' in data:
                data = data.split(',')
            
            ## empty array for output
            data_array = []
            ## loop through args
            for arrData in data:
                ## clean up data
                arrData = arrData.lstrip().rstrip()
                test = self.MEMORY.var_get(arrData)
                
                ## if we dont have var get corret type
                if test == False:
                    arrData = self.MEMORY.type_guess(arrData)
                    
                    ## check if string if so remove \"
                    if type(arrData) == str and '"' in arrData:
                        arrData = arrData.replace('"','')

                else:
                    arrData = test[1]
                    
                data_array.append(arrData)
                
            self.MEMORY.var_add(name, "array", data_array)

    def blue_dict(self, args):
        pass

    def blue_sleep(self, args):
        time_to_sleep = 0
        args = args.lstrip().rstrip() ## just so that we can clean the string
        
        temp = self.MEMORY.var_get(args)
        
        if temp == False:
            temp = self.MEMORY.type_guess(args)
            if type(temp) != int:
                raise Exception("Incompatable type and isn't int")
            time_to_sleep = temp
        else:
            time_to_sleep = temp[1]
        
        time.sleep(time_to_sleep)      


    def blue_print(self, args):
        if "\"" in args:
            ## print string
            print(args.replace("\"", ""))
            return
        out = self.MEMORY.var_get(args)
        if out == False:
            raise Exception(f"Variable '{args}' does not exist")
        
        if type(out[1]) == bs_types.BLUE_ARRAY:
            print(out[1].data)
            return
        
        if type(out[1]) == str and '\"' in out[1]:
            print(out[1].replace('"',''))
            return
        
        if type(out) == list:
            print(out[1])
            return
        
        print(out)    
    
def include_file(filename, current_file):
    if not filename.endswith(".bs"):
        filename += ".bs"

    if filename == current_file:
        raise Exception("Cannot include self")

    if UPL.Core.file_exists(filename):
        return UPL.Core.file_manager.clean_read(filename)

    else:
        raise Exception(f"Cannot find file '{filename}'")