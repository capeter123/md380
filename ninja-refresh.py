#!/usr/bin/python

import re, os.path

# This little script scans "build.ninja" for lines like this:

#CC: stm/fault.c
#CC: stm/gpio.c
#CC: stm/interrupt.c
#CC: stm/led.c
#CC: stm/rcc.c
#CC: stm/system_stm32f4xx.c
#AR: stm.a

# - for every "CC:" line, it will generate a "build obj/fault.o: cc stm/fault.c" rule.
#
# - for the final "AR:" line, it will generate a "build obj/stm.a: ar
#   OBJS" where OBJS is the list of all objects from the previous build lines
#
# That way I don't have to manage the long library lines by hand



rxCommand = re.compile(r'^#([A-Z]+):\s+(\S+)\s*$')
rxComment = re.compile("^#")
rxBuild = re.compile("^build")

IDLE = 0
CMD = 1
state = IDLE
out = []
files = []

for s in open("build.ninja").readlines():
	m = rxCommand.search(s)
	if m:
		out.append("#%s: %s\n" % m.groups())
		state = CMD
		rule = m.group(1).lower()
		source = m.group(2)
		dest = os.path.splitext(source)[0]
		# print "RULE:", rule
		# print "SOURCE:", source
		# print "DEST:", dest
		if rule in ("cxx", "as") or rule.startswith("cc"):
			dest = os.path.join("obj", os.path.basename(dest) + ".o")
			s = "build %s: %s %s" % (dest, rule, source)
			files.append( (dest, s) )
		elif rule == "ar":
			dest = os.path.join("obj", os.path.basename(dest) + ".a")
			out.append("# The following entries have been auto-generated by ninja-refresh:\n")
			files.sort()
			buildline = ["build %s: %s" % (dest, rule)]
			for s in files:
				out.append(s[1] + "\n")
				buildline.append(s[0])
			files = []
			out.append(" ".join(buildline) + "\n")
		continue
	m = rxComment.search(s)
	if m and state == CMD:
		continue
	m = rxBuild.search(s)
	if m and state == CMD:
		continue
	state = IDLE
	out.append(s)

f = open("build.ninja", "w")
f.write("".join(out))

