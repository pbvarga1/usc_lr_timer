Feature: Login
   The login window


Scenario: Selecting Journal
    Given the window
    When I select a journal
    Then there are names


Scenario: Valid Login
    Given the window
    When I select a journal
    And select the name "Vincent"
    And type the pin "1234"
    And click login
    Then the dialog is accepted


Scenario: Invalid Login
    Given the window
    When I select a journal
    And select the name "Vincent"
    And type the pin "5678"
    And click login
    Then an error is box is shown
