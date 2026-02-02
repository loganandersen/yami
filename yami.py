#!/usr/bin/python3 
#yami.py
#yami is the head of a shortcut program . you type yami and then type the name of the shortcut to run a script that opens up the shortcuts. ie. yami test , which would run a script for test 

import os
import argparse
import subprocess 
import sys
import shutil

SHORTCUTSDIR = os.path.expanduser('~/.programs/shortcuts/programs') 
HOMEFOLDER = os.path.expanduser('~/.programs/shortcuts')

# I used to have a TEXTEDITOR varible but I wanted to make sure it
# always gave a feasable editor. I only want the error message to
# activate when I do an operation that edits a file, which is why I've
# decided to turn it into a function since the error message will show
# up whenever there is a function call. If I only wanted the error
# mesage to trigger when there was no text editor, the only
# alternative would be to do a check whenever there was a text editor,
# or to read the parseargs results and check a list of flags that use
# the editor.
def get_text_editor() :
    editor = os.getenv("EDITOR")
    if editor in (None, '')  :
        if shutil.which("editor") != None :
            editor = "editor"
        else :
            editor = "ed"
        print("Warning: No text editor found, defaulting to", editor, "please set the EDITOR environment variable to fix this", file=sys.stderr)
    return editor



def get_file_links(document) :
    """reads a document and returns a dict that links the program names to the script"""  
    dictionary = dict() 
    try :
        with open(document,'r') as f :
            for line in f : 
                lines = line.partition('⟶') 
                program = lines[0].strip() 
                script = lines[2].strip() 
                dictionary[program] = script                
    except FileNotFoundError : 
        print('file not found, this may be because you are creating a new file or it could be because it is gone') 
    return dictionary

def new_link(document,program,script) :
    with open(document,'a') as f :
        f.write(f'{program} ⟶ {script}\n') 
    return 

def new(results,edit,links) :
    if results.filename != None : 
        remove_link(results.file,results.program)
        if results.resolve :
            filename = links[results.filename]
        else : 
            filename = results.filename 
        new_link(results.file,results.program,filename) 
        filepath = os.path.join(SHORTCUTSDIR,filename)
        if edit : 
            subprocess.run([get_text_editor() , filepath])
        #chmod 755 
        if not results.jump : 
            os.chmod(filepath , int('111101101',2))
    else :
        print('there is no filename, exiting program') 
        sys.exit(2) 

def remove_link(document,name,func=str.startswith) :
    with open(document,'r') as f :
        #remove all the instances where the first line is the things name and then recombine
        newdoc = ''.join(filter(lambda line : not func(line.strip(),name) ,f))
    #rewrite the document
    with open(document,'w') as f :
        f.write(newdoc)

def run(results,links,frontprogram = '',jump = False) : 
    args = []
    if not results.program : 
        print(f'You did not enter the program name for something that requires a program name exiting')
        sys.exit(2) 
    if frontprogram : 
        args.append(frontprogram)

    if results.program in links : 
        if jump : 
            os.chdir(os.path.expanduser(links[results.program]))
            subprocess.run(frontprogram) 
        else : 
            args.append(os.path.join(SHORTCUTSDIR,links[results.program]))
            try :
                subprocess.run(args) 
            except KeyboardInterrupt :
                pass
    else : 
        print(f'{results.program} is not in {results.file} exiting')
        sys.exit(2) 

def main() : 

    DEFAULTFILE = os.path.expanduser('~/.programs/shortcuts/defaut.dat') 
    JUMPFILE = os.path.expanduser('~/.programs/shortcuts/jump.dat') 
    
    parser = argparse.ArgumentParser(description='''yami is a program for shortcuts
            it has two functions. Its primary purpose is to act as a namespace for 
            simple scripts that do not take arguments. Its secondary purpose (called jump mode)
            is to allow the user to jump to certain directories using the shortcut names.''') 

    parser.add_argument('program',nargs='?',help='the name of the shortcut')
    parser.add_argument('filename',default=None,nargs='?',help='the name of the file that the shortcut turns into. In jump mode this is the name of the directory instead' ) 
    parser.add_argument('-f','--file',default=DEFAULTFILE) 
    parser.add_argument('-j','--jump','--jump-mode', action='store_true') 
    parser.add_argument('-r','--resolve',action='store_true') 

    modes = parser.add_mutually_exclusive_group() 
    modes.add_argument('-n','--new',action='store_true') 
    modes.add_argument('-R','--run',action='store_true') 
    modes.add_argument('-l','--link',action='store_true') 
    modes.add_argument('-e','--edit',action='store_true') 
    modes.add_argument('-d','--delete',action='store_true') 
    modes.add_argument('--deletefile','--df',action='store_true') 
    modes.add_argument('-p','--print', choices=('list','l','homefolder','scriptdir','file','names')) 
    modes.add_argument('--folderedit',action='store_true') 
    
    results = parser.parse_args() 


    if results.jump : 
        if results.file == DEFAULTFILE : 
            results.file = JUMPFILE

        if results.edit or results.new or results.deletefile : 
            print("edit, new, or deletefile do not work with jump\n exiting program")
            sys.exit(2)

    if results.resolve and not (results.link or results.deletefile) :
        print("resolve only makes sense when link or deletefile flags are active \n exiting program")
        sys.exit(2)



    links = get_file_links(results.file) 

    if results.new :
        new(results,edit=True,links=links) 
    elif results.link : 
        new(results,edit=False,links=links)  
    elif results.delete :
        remove_link(results.file,results.program)
    elif results.edit : 
        run(results,links,get_text_editor())
    elif results.print :
        command = results.print
        if command in ('list', 'l') :
            with open(results.file,'r') as f :
                print(f.read().rstrip()) 
        elif command == 'homefolder' :
            print(HOMEFOLDER) 
        elif command == 'names' :
            for name in links : 
                print(name) 

        elif command == 'scriptdir' :
            #print the directory with hidden and backup files removed 
            print('\n'.join(
                filter ( lambda string : not (string.startswith('.') or string.endswith('~') ) , os.listdir(SHORTCUTSDIR) )
                ))
        elif command == 'file' :
            program = results.program 
            if program == None :
                print('you need to specify a file to print for -p file to work') 
                sys.exit(2) 

            elif program not in links :
                print(f'{program} was not found in {results.file}')
                sys.exit(2) 

            else :
                if results.jump : 
                    print(links[results.program])
                else :
                    with open(os.path.join(SHORTCUTSDIR,links[results.program]),'r') as f :
                        print(f.read().rstrip()) 
    elif results.folderedit :
        subprocess.run([get_text_editor(),DEFAULTFILE]) 
    elif results.deletefile : 
        if results.resolve :
            program = links.get(results.program,None)
        else : 
            program = results.program
        if program == None :
            print('this argument requires that you insert the filename that you want to delete') 
            sys.exit(2) 
        else : 
            if program in os.listdir(SHORTCUTSDIR) :
                os.remove(os.path.join(SHORTCUTSDIR,program)) 
                remove_link(results.file,program,str.endswith)
                print(f'{program} has been removed') 
            else : 
                print(f'{program} not in {SHORTCUTSDIR}') 
    elif results.jump : 
        run(results,links,frontprogram = 'bash',jump = True)
    else :
        try : 
            run(results,links)
        except KeyboardInterrupt :
            pass



main() 
