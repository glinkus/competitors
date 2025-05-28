module.exports = {
  testEnvironment: "jsdom",
  testMatch: ["**/tests/js/**/*.test.js"],
  transform: {
    "^.+\\.js$": "babel-jest"
  },
  transformIgnorePatterns: ["/node_modules/"]
};
