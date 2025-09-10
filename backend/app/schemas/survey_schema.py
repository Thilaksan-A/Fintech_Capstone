from marshmallow import Schema, fields, validate


class SurveySchema(Schema):
    stress_response = fields.Str(
        required=True,
        validate=validate.OneOf(
            [
                "Not knowing what to do when the market drops",
                "Investing without having enough information",
                (
                    "Not knowing who to trust when friends and media say different"
                    " things"
                ),
                "Fear of losing money",
                "I don't get stressed, I stay calm while investing",
            ],
        ),
    )

    emotional_reaction = fields.Str(
        required=True,
        validate=validate.OneOf(
            [
                "I would sell immediately",
                "I'd panic but wouldn't know what to do",
                "I would check the source and decide accordingly",
                "I wouldn't be affected by this kind of news",
            ],
        ),
    )

    risk_perception = fields.Str(
        required=True,
        validate=validate.OneOf(
            [
                "Something I cannot afford to lose",
                "Uncertainty but also potential gain",
                "Manageable fluctuations",
                "There's always some risk where there's opportunity",
            ],
        ),
    )

    income_vs_investment_balance = fields.Str(
        required=True,
        validate=validate.OneOf(
            [
                "Less than 5%",
                "Between 5% and 15%",
                "Between 15% and 30%",
                "More than 30%",
            ],
        ),
    )

    debt_situation = fields.Str(
        required=True,
        validate=validate.OneOf(
            [
                "Yes, I make monthly payments",
                "Yes, but it's at a low level",
                "No, I have no debt",
                "I do, but it doesn't affect my investment decisions",
            ],
        ),
    )

    investment_experience = fields.Str(
        required=True,
        validate=validate.OneOf(
            [
                "Stocks",
                "Cryptocurrency",
                "Term deposits / gold",
                "Real estate",
                "I haven't invested before",
            ],
        ),
    )

    investment_motivation = fields.Str(
        required=True,
        validate=validate.OneOf(
            [
                "To generate passive income",
                "For future large expenses (house, car, etc.)",
                "For retirement",
                "To try new things",
                "To learn and have fun",
            ],
        ),
    )

    knowledge_level = fields.Str(
        required=True,
        validate=validate.OneOf(
            [
                "I'm a beginner, I have very little knowledge",
                "I'm at an intermediate level",
                "I understand concepts like technical analysis",
                "I've been investing for a long time, I'm experienced",
            ],
        ),
    )

    investment_personality = fields.Str(
        required=True,
        validate=validate.OneOf(
            [
                "Conservative: I avoid taking risks",
                "Balanced: I can handle some risk, but nothing extreme",
                "Aggressive: I'm drawn to high-risk, high-reward opportunities",
                "Intuitive: I often follow my instincts",
                "Strategic: I plan and execute with discipline",
            ],
        ),
    )
