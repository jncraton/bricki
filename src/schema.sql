.timer on

create table if not exists set_transactions (
  id integer primary key,
  date timestamp default current_timestamp,
  set_num varchar(16),
  quantity smallint,
  notes varchar(255),
  foreign key (set_num) references sets(set_num)
);

create table if not exists part_transactions (
  id integer primary key,
  date timestamp default current_timestamp,
  part_num varchar(16),
  color_id smallint,
  quantity smallint,
  from_set_num varchar(16),
  notes varchar(255),
  foreign key (part_num) references parts(part_num),
  foreign key (color_id) references parts(color_id),
  foreign key (from_set_num) references sets(set_num)
);

drop view if exists my_set_parts;
create view if not exists my_set_parts
as
select 
  part_num,
  color_id,
  sum(set_parts.quantity * set_transactions.quantity) as quantity
from set_transactions
left outer join set_parts on
  set_parts.set_num = set_transactions.set_num
group by part_num, color_id;

drop view if exists my_parts;
create view if not exists my_parts
as
select part_num, color_id, sum(quantity) as quantity from (
  select part_num, color_id, quantity
  from part_transactions
  union all
  select part_num, color_id, quantity
  from my_set_parts
);