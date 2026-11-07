CREATE TABLE session (id TEXT PRIMARY KEY, directory TEXT);
CREATE TABLE message (id TEXT PRIMARY KEY, session_id TEXT, time_created INTEGER, data TEXT);
INSERT INTO session VALUES ('oc-session','/fixture');
INSERT INTO message VALUES ('oc-call','oc-session',1793959200000,'{"role":"assistant","modelID":"beam-free","providerID":"opencode","tokens":{"input":80,"output":15,"reasoning":5,"cache":{"read":20,"write":0}},"cost":0,"time":{"created":1793959200000,"completed":1793959202000},"finish":"stop"}');
INSERT INTO message VALUES ('oc-user','oc-session',1793959200000,'{"role":"user","content":"SYNTHETIC_PRIVATE_TEXT"}');
