.timer on

create table if not exists part_details (
  part_num varchar(16) primary key,
  part_url varchar(128),
  part_img_url varchar(128),
  bricklink_id varchar(16),
  brickowl_id varchar(16),
  ldraw_id varchar(16),
  lego_id varchar(16),
  foreign key (part_num) references sets(part_num)
);

create table if not exists set_transactions (
  date timestamp default current_timestamp,
  set_num varchar(16),
  quantity smallint,
  notes varchar(255),
  foreign key (set_num) references sets(set_num)
);

create table if not exists part_transactions (
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

create table if not exists part_bins (
  part_num varchar(16),
  color_id smallint,
  bin_id varchar(64),
  -- A null value indicates that the part is stored alone
  -- Other values are used to group parts together
  section_id varchar(64),
  foreign key (part_num) references parts(part_num),
  foreign key (color_id) references parts(color_id),
  primary key (part_num, color_id)
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
)
group by part_num, color_id;