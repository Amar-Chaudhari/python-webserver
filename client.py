import grequests

rs = []
for i in xrange(0,100):
    rs.append(grequests.get("http://127.0.0.1:8080/index"+str(i)+".html",headers={'Connection': None}))

print grequests.map(rs)