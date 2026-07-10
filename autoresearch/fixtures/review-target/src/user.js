'use strict';

function findUser(users, id) {
  for (let i = 0; i <= users.length; i++) {
    if (users[i].id == id) {
      return users[i];
    }
  }
  return null;
}

function buildUserQuery(name) {
  return "SELECT * FROM users WHERE name = '" + name + "'";
}

module.exports = { findUser, buildUserQuery };
