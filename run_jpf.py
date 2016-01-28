import argparse
import textwrap
import json
import csv
import os
import glob
import subprocess

def processFile(bench, result, tool):
    stats = {"tool": tool, "ans":"", "time":"", "mem":"", "inst":""}
    if result is None:
        stats.update({"ans":"ERR"})
        return {bench:stats}, stats
    if tool == "JPF":
        for r in result.splitlines():
            if 'no errors detected' in r:
                stats.update({"ans":"SAFE"})
            if 'elapsed time' in r:
                t = r.split()
                time = t[len(t)-1]
                stats.update({"time":str(time)})
            if 'max memory' in r:
                t = r.split()
                mem = t[len(t)-1]
                stats.update({"mem":str(mem)})
            if 'instructions' in r:
                t = r.split()
                ins = t[len(t)-1]
                stats.update({"inst":str(ins)})
            if 'java.lang.AssertionError' in r:
                stats.update({"ans":"CEX"})
    elif tool == "JAYHORN":
        if "checker says true" in result:
            stats.update({"ans":"SAFE"})
        if "checker says false" in result:
            stats.update({"ans":"CEX"})
    return {bench:stats}, stats


config = """ target=Main
 classpath=${jpf-core}/../../benchmarks/MinePump/spec1-5/%s
"""

JPF = "./jpf-travis/jpf-core/build/RunJPF.jar"
JAYHORN = "./jayhorn/jayhorn/build/libs/jayhorn.jar"


def runJar(jar):
    try:
        p = subprocess.Popen(jar, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        result, _ = p.communicate()
        return result
    except Exception as e:
        print str(e)
        return None


def runBench(args):
    dr = args.directory
    viz_html = ""
    all_dir = [os.path.join(dr, name)for name in os.listdir(dr) if os.path.isdir(os.path.join(dr, name)) ]
    all_results = {}
    for d in all_dir:
        print "Benchmark:\t " + str(d)
        tmp = d.split("/")
        bench = tmp[len(tmp)-1]
        jpf = glob.glob(os.path.abspath(d) + os.sep + "*.jpf")
        cmd_jayhorn = ['java', "-jar", JAYHORN, "-solver", "z3",  "-t", "60", "-j", d]
        if len(jpf) == 1:
            # file = fileinput.FileInput(jpf[0], inplace=True, backup='.bak')
            # for line in file:
            #     print line.replace("/Users/teme/Documents/GitHub/jayhorn/jayhorn/build/resources/test/", "${jpf-core}/../../benchmarks/")
            # file.close()
            cmd_jpf = ['java', "-jar", JPF, "+shell.port=4242", jpf[0]]
            jpf_result = runJar(cmd_jpf)
            jayhorn_result = runJar(cmd_jayhorn)
            jpf_ans, jpf_stats = processFile(bench, jpf_result, "JPF")
            jayhorn_ans, jayhorn_stats = processFile(bench, jayhorn_result, "JAYHORN")
            print "JPF RESULT:\t" + str(jpf_stats)
            print "JAYHORN RESULT:\t" + str(jayhorn_stats)
            print "---------------------"
        else:
            jayhorn_result = runJar(cmd_jayhorn)
            jayhorn_ans, jayhorn_stats = processFile(bench, jayhorn_result, "JAYHORN")
            print "JPF RESULT:\t" + "NO JPF CONFIG"
            print "JAYHORN RESULT:\t" + str(jayhorn_stats)
            print "---------------------"

            #all_results.update(ans)
    # print "---- SUMMARY ----"
    # print all_results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='Bench Analysis Utils',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent('''\
                   Bench Analysis Utils
            --------------------------------
            '''))
    #parser.add_argument ('file', metavar='BENCHMARK', help='Benchmark file')
    parser.add_argument ('directory', metavar='DIR', help='Benchmark dirs')
    #parser.add_argument('-fc', '--fc', required=False, dest="fc", action="store_true")
    #parser.add_argument('-err', '--err', required=False, dest="err", action="store_true")

    args = parser.parse_args()
    try:
        runBench(args)
    except Exception as e:
        print str(e)
