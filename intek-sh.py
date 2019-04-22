#!/usr/bin/env python3
from os import environ, chdir, getcwd
from os.path import isdir, isfile, exists, join
from subprocess import run


class Shell:
    def __init__(self):
        self.env = environ.copy()
        self.builtins = ['cd', 'printenv', 'export', 'unset', 'exit']
        self.enter_keys = ['|', '\\', '||', '&&', '\\\\&&', '\\\\||']
        self.exit = False
        self.inputs = ''
        self.pipes = []

    def get_inputs(self):
        """Get user input."""
        self.inputs = input('intek-sh$ ').split()
        while len(self.inputs) > 1 and self.inputs[-1] in self.enter_keys:
            self.inputs += input('> ').split()
        self.inputs = ' '.join(
            [item for item in self.inputs if item != '\\'])

    def get_pipes(self):
        """Get each command vs argument."""
        self.pipes = [item.split() for item in self.inputs.split(' | ')]

    def execute_cd(self, arg):
        """Execute change directory."""
        if arg:
            chdir(arg[0])
        else:
            if 'HOME' not in self.env:
                print('intek-sh: cd: HOME not set')
            else:
                chdir(self.env['HOME'])

    def execute_printenv(self, arg):
        """Execute print environment."""
        if arg:
            for item in arg:
                if item in self.env:
                    print(self.env[item])
        else:
            for key, value in self.env.items():
                print(key + '=' + value)

    def execute_export(self, arg):
        """Execute export command."""
        for item in arg:
            if '=' not in item:
                self.env[item] = ''
            else:
                key, value = item.split('=')
                self.env[key] = value

    def execute_unset(self, arg):
        """Execute unset command."""
        for item in arg:
            if item in self.env:
                del self.env[item]

    def execute_exit(self, arg):
        """Execute exit command."""
        print('exit')
        if len(arg) == 1 and not arg[0].isdigit():
            print('intek-sh: exit:')
        self.exit = True

    def execute_builtin(self, cmd, arg):
        if cmd == 'cd':
            self.execute_cd(arg)
        elif cmd == 'printenv':
            self.execute_printenv(arg)
        elif cmd == 'export':
            self.execute_export(arg)
        elif cmd == 'unset':
            self.execute_unset(arg)
        elif cmd == 'exit':
            self.execute_exit(arg)

    def execute_external(self, cmd, arg):
        """Execute external binary file."""
        if './' in cmd:
            try:
                run(cmd)
            except PermissionError:
                print('intek-sh: ' + cmd + ': Permission denied')
            except FileNotFoundError:
                print('intek-sh: ' + cmd + ': command not found')
        elif 'PATH' in self.env:
            found = False
            for path in self.env['PATH'].split(':'):
                command_path = join(path, cmd)
                if exists(command_path):
                    found = True
                    run([command_path] + arg)
                    break
            if not found:
                print('intek-sh: ' + cmd + ': command not found')
        else:
            print('intek-sh: ' + cmd + ': command not found')

    def execute_command(self, cmd, arg):
        if cmd in self.builtins:
            self.execute_builtin(cmd, arg)
        else:
            self.execute_external(cmd, arg)

    def run_repl_loop(self):
        """Run REPL loop."""
        while not self.exit:
            try:
                self.get_inputs()
                self.get_pipes()
                [self.execute_command(pipe[0], pipe[1:])
                    for pipe in self.pipes if pipe]
            except EOFError:
                break


def main():
    minish = Shell()
    minish.run_repl_loop()


if __name__ == '__main__':
    """Run the main program"""
    try:
        main()
    except Exception:
        pass
