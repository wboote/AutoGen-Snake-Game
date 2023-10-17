from autogen import AssistantAgent, UserProxyAgent, config_list_from_json, GroupChat, GroupChatManager

# Load the configuration for GPT-4 from a JSON file
config_list_gpt4 = config_list_from_json(
    "./OAI_CONFIG_LIST.json",
    filter_dict={
        "model": ["gpt-4-0613", "gpt-4-32k", "gpt-4", "gpt-4-0314"],
    },
)

# Define the GPT-4 configuration parameters
gpt4_config = {
    "seed": 42,
    "temperature": 0,
    "config_list": config_list_gpt4,
    "request_timeout": 1200,
}

# Define the common working directory for all agents
working_directory = "job_files"

# Initialize the Runner agent, responsible for providing feedback on running the application
runner = UserProxyAgent(
    name="Runner",
    system_message="Runner: Your role is to provide feedback on running the application. Collaborate with the Application Designer to ensure the application meets desired expectations.",
    code_execution_config={
        "work_dir": working_directory,
        "use_docker": False,
        "timeout": 120,
        "last_n_messages": 1,
    },
)

# Initialize the Application Designer agent, responsible for designing the application
app_designer = AssistantAgent(
    name="Application_Designer",
    llm_config=gpt4_config,
    system_message="Application Designer: Write and save a program in python that recursively searches .java files for session.createCriteria() calls.  For these calls, copy the code block until session.list() is called.  Pass the copied code block to the openai gpt-4 rest api and get it to convert the Hibernate native code block to JPA compatible.  Save the resultant converted code block., ensuring all details are documented in 'app_design.txt'. Collaborate with the Runner to align the design with feedback and expectations."
)

# Initialize the Programmer agent, responsible for coding the application
programmer = AssistantAgent(
    name="Programmer",
    llm_config=gpt4_config,
    system_message="Programmer: Code the application and save it in the working directory. For code execution, collaborate with the Code Executor. If feedback is needed, consult the Application Tester."
)

# Initialize the Application Tester agent, responsible for testing the application
app_tester = UserProxyAgent(
    name="Application_Tester",
    system_message="Application Tester: Test the application and provide feedback on application mechanics and user experience. Report any bugs or glitches. Collaborate with the Programmer for any necessary adjustments.",
    code_execution_config={
        "work_dir": working_directory,
        "use_docker": False,
        "timeout": 120,
        "last_n_messages": 3,
    },
    human_input_mode="ALWAYS",
)

# Initialize the Code Executor agent, responsible for executing the application code
code_executor = UserProxyAgent(
    name="Code_Executor",
    system_message="Code Executor: Execute the provided code from the Programmer in the designated environment. Report outcomes and potential issues. Ensure the code follows best practices and recommend enhancements to the Programmer.",
    code_execution_config={
        "work_dir": working_directory,
        "use_docker": False,
        "timeout": 120,
        "last_n_messages": 3,
    },
    human_input_mode="NEVER",
)

# Set up the group chat with all the agents
groupchat = GroupChat(
    agents=[runner, app_tester, app_designer, programmer, code_executor],
    messages=[],
    max_round=150
)

# Create a manager for the group chat using the GPT-4 configuration
manager = GroupChatManager(groupchat=groupchat, llm_config=gpt4_config)

# Start the conversation with the Runner's message
runner.initiate_chat(
    manager,
    message="Let's design, implement and save a python program that converts .java Hibernate native codeblocks to JPA compatible. I aim for it to be challenging."
)
