USE capstone;

select *
from user_info;

select count(*)
from user_info
where id = "test" and pw = "test";


insert user_info(id, pw, name, email)
values ("testid", "testpw", "testname", "testemail");

select * 
from user_info;

