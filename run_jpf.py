import argparse
import textwrap
import json
import csv
import os
import glob
import subprocess

def processFile(bench, result):
    stats = {"ans":"", "time":"", "mem":"", "ins":""}
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
            stats.update({"ins":str(ins)})
        if 'java.lang.AssertionError' in r:
            stats.update({"ans":"CEX"})
    return {bench:stats}, stats


config = """ target=Main
 classpath=${jpf-core}/../../benchmarks/MinePump/spec1-5/%s
"""

JPF = "./jpf-travis/jpf-core/build/RunJPF.jar"
JAYHORN = "./jayhorn/jayhorn/build/libs/jayhorn.jar"

def runJar(jar):
    try:
        print "Running " + jar
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
        print d
        tmp = d.split("/")
        bench = tmp[len(tmp)-1]
        jpf = glob.glob(os.path.abspath(d) + os.sep + "*.jpf")
        if len(jpf) == 1:
            # file = fileinput.FileInput(jpf[0], inplace=True, backup='.bak')
            # for line in file:
            #     print line.replace("/Users/teme/Documents/GitHub/jayhorn/jayhorn/build/resources/test/", "${jpf-core}/../../benchmarks/")
            # file.close()
            cmd_jpf = ['java', "-jar", JPF, "+shell.port=4242", jpf[0]]
            cmd_jayhorn = ['java', "-jar", JAYHORN, "-solver", "z3",  "-j", d]
            jpf_result = runJar(JPF)
            jayhorn_result = runJar(JAYHORN)
            if jpf_result:
                print "-------  JPF -------"
                ans, stats = processFile(bench, jpf_result)
                print "Benchmark: " + bench
                print "Result:" + str(stats)
                print "---------------------"
                all_results.update(ans)
            if jayhorn_result:
                print "-------  JPF -------"
                print jayhorn_result
                print "---------------------"
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
