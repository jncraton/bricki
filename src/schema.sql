.timer on

create table if not exists transactions (
  id integer primary key,
  date timestamp default current_timestamp,
  set_num varchar(16),
  part_num varchar(16),
  color_id smallint,
  quantity smallint,
  lot varchar(32),
  notes varchar(255),
  foreign key (set_num) references sets(set_num),
  foreign key (part_num) references parts(part_num),
  foreign key (color_id) references parts(color_id)
);

create view if not exists my_parts
as
select p as part_num, c as color_id, sum(q) as quantity from (
  select
    part_num as p,
    color_id as c,
    quantity as q
  from transactions
  where transactions.set_num is null
  union
  select 
    set_parts.part_num as p,
    set_parts.color_id as c,
    set_parts.quantity * transactions.quantity as q
  from transactions
  left outer join set_parts on
    set_parts.set_num = transactions.set_num
  where transactions.set_num not null
) group by part_num, color_id;