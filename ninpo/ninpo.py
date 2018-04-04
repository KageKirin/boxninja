# Ninpo - functions to generate ninja rules

import ninja_syntax

def create_ninjascroll(buildfile):
    # create ninja file
    ninjaWriter = ninja_syntax.Writer(buildfile)
    ninjaWriter.variable('ninja_required_version', '1.3')
    ninjaWriter.newline()
    return ninjaWriter


def create_rule(ninjaWriter, name, cmd):
    # create a rule for given command
    ninjaWriter.rule(name, command=cmd)
    ninjaWriter.newline()
    return name


def create_target(ninjaWriter, rule, infiles, outfile):
    # create a target for given rule
    target = ninjaWriter.build(outfile, rule, infiles)
    ninjaWriter.newline()
    return target
