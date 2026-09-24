import subprocess,sys
p=subprocess.run([r"C:\Users\Administrator\.workbuddy\binaries\python\versions\3.13.12\python.exe",r"D:\vcp_hunter\产业链投研\scripts\build_blocknew_weekly_report.py"],capture_output=True)
out=(p.stdout.decode('utf-8',errors='replace')+p.stderr.decode('utf-8',errors='replace'))
open(r"D:\vcp_hunter\产业链投研\outputs\build_weekly_out.txt","w",encoding="utf-8").write(out)