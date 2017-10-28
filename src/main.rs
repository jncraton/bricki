extern crate sqlite;

use sqlite::{Connection, State, Type, Value};

fn main() {
  let connection = sqlite::open("dist/bricks.db").unwrap();

  let mut cursor = connection
    .prepare("SELECT name, id FROM colors where id < ?")
    .unwrap()
    .cursor();
  
  cursor.bind(&[Value::Integer(50)]).unwrap();
  
  while let Some(row) = cursor.next().unwrap() {
      println!("name = {}", row[0].as_string().unwrap());
      println!("age = {}", row[1].as_integer().unwrap());
  }
}