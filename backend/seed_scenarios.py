from apps.training.models import Scenario

# Delete existing scenarios
Scenario.objects.all().delete()

# Create Job Interview scenario
Scenario.objects.create(
    title="Job Interview",
    description="Practice professional interview skills in a realistic job interview setting.",
    difficulty="advanced",
    system_prompt="""You are an HR manager conducting a job interview. Be professional, ask relevant questions about the candidate's experience, skills, and career goals. Evaluate their communication skills and confidence. Ask follow-up questions based on their responses.""",
    initial_message="Hello! Thank you for coming in today. Please have a seat. Can you start by telling me a bit about yourself and why you're interested in this position?",
    objectives=[
        "Introduce yourself professionally",
        "Discuss your relevant experience",
        "Ask thoughtful questions about the role",
        "Demonstrate confidence and clear communication"
    ],
    icon="briefcase",
    is_active=True
)

# Create Ordering Coffee scenario
Scenario.objects.create(
    title="Ordering Coffee",
    description="Practice everyday conversation skills while ordering at a coffee shop.",
    difficulty="beginner",
    system_prompt="""You are a friendly barista at a coffee shop. Help the customer order their drink, suggest options, and engage in light conversation. Be patient and encouraging.""",
    initial_message="Hi there! Welcome to our coffee shop. What can I get started for you today?",
    objectives=[
        "Greet the staff politely",
        "Order your drink with specific details",
        "Ask about options or recommendations",
        "Complete the transaction"
    ],
    icon="coffee",
    is_active=True
)

# Create Hotel Check-in scenario
Scenario.objects.create(
    title="Hotel Check-in",
    description="Navigate the hotel check-in process and request services in English.",
    difficulty="intermediate",
    system_prompt="""You are a hotel receptionist. Help the guest check in, confirm their reservation, explain hotel amenities, and answer any questions they have. Be professional and hospitable.""",
    initial_message="Good afternoon! Welcome to our hotel. May I have your name for the reservation, please?",
    objectives=[
        "Provide your reservation details",
        "Ask about room amenities",
        "Inquire about hotel services",
        "Confirm check-in information"
    ],
    icon="hotel",
    is_active=True
)

print(f"Created {Scenario.objects.count()} scenarios successfully!")
for scenario in Scenario.objects.all():
    print(f"- {scenario.title} ({scenario.difficulty})")
