Feature: Order Transaction
  Test related to Order transactions

  Scenario Outline: Verify Order success message shown in details page
    Given place the item order with <username> and <password>
    And the user is on landing plage
    When I login to portal with <username> and <password>
    And navigate to orders page
    And select the orderId
    Then order message is successfully displayed
    Examples:
      | username | password |
      | jhonatanfc94@gmail.com | Testing1 |