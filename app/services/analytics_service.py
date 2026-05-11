from app.models import Category, Transaction
from app.schemas import SavingsPlanResponse


def calculate_average_monthly_expenses(
    transactions: list[Transaction],
    categories: list[Category],
) -> tuple[float, dict[str, float]]:
    """
    Calculate average monthly expenses and expenses by category.

    Only transactions from categories with type 'expense' are used.
    """
    expense_category_ids = {
        category.id
        for category in categories
        if category.type == "expense"
    }

    expense_category_names = {
        category.id: category.name
        for category in categories
        if category.type == "expense"
    }

    expense_transactions = [
        transaction
        for transaction in transactions
        if transaction.category_id in expense_category_ids
    ]

    if not expense_transactions:
        return 0, {}

    months = {
        (transaction.date.year, transaction.date.month)
        for transaction in expense_transactions
    }

    months_count = max(len(months), 1)

    expenses_by_category: dict[str, float] = {}

    for transaction in expense_transactions:
        category_name = expense_category_names[transaction.category_id]
        expenses_by_category[category_name] = (
            expenses_by_category.get(category_name, 0) + transaction.amount
        )

    total_expenses = sum(transaction.amount for transaction in expense_transactions)
    average_monthly_expenses = total_expenses / months_count

    average_expenses_by_category = {
        category_name: amount / months_count
        for category_name, amount in expenses_by_category.items()
    }

    return round(average_monthly_expenses, 2), average_expenses_by_category


def generate_savings_plan(
    monthly_income: float,
    target_amount: float,
    months: int,
    transactions: list[Transaction],
    categories: list[Category],
) -> SavingsPlanResponse:
    """
    Generate a savings plan based on income, goal and user's expenses.

    The function calculates required monthly savings, average expenses,
    free money and recommendations.
    """
    monthly_saving_required = target_amount / months

    average_monthly_expenses, expenses_by_category = (
        calculate_average_monthly_expenses(
            transactions,
            categories,
        )
    )

    free_money = monthly_income - average_monthly_expenses
    is_goal_realistic = free_money >= monthly_saving_required

    recommendations: list[str] = []

    if is_goal_realistic:
        recommendations.append("Цель достижима без сокращения расходов")
    else:
        missing_amount = monthly_saving_required - free_money

        sorted_categories = sorted(
            expenses_by_category.items(),
            key=lambda item: item[1],
            reverse=True,
        )

        if not sorted_categories:
            recommendations.append(
                "Недостаточно данных о расходах для рекомендаций"
            )
        else:
            remaining_amount = missing_amount

            for category_name, category_expense in sorted_categories:
                if remaining_amount <= 0:
                    break

                suggested_cut = min(
                    category_expense * 0.3,
                    remaining_amount,
                )

                if suggested_cut > 0:
                    recommendations.append(
                        "Сократите расходы в категории "
                        f"'{category_name}' примерно на "
                        f"{round(suggested_cut, 2)}"
                    )
                    remaining_amount -= suggested_cut

            if remaining_amount > 0:
                recommendations.append(
                    "Даже после сокращения крупных категорий цель может быть "
                    "сложнодостижимой. Увеличьте срок накопления или уменьшите "
                    "целевую сумму."
                )

    return SavingsPlanResponse(
        monthly_saving_required=round(monthly_saving_required, 2),
        average_monthly_expenses=round(average_monthly_expenses, 2),
        free_money=round(free_money, 2),
        is_goal_realistic=is_goal_realistic,
        recommendations=recommendations,
    )
