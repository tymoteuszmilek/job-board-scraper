import regex as re

# Set of technologies in lowercase for case-insensitive matching
tech_stacks = {
    'Python', 'Django', 'Flask', 'JavaScript', 'React', 'Angular', 'Vue', 'Node.js', 'Express',
    'Ruby', 'Rails', 'Java', 'Spring', 'Kotlin', 'Swift', 'Objective-C', 'C', 'C++', 'C#',
    '.NET', 'PHP', 'Laravel', 'Symfony', 'Go', 'Rust', 'Scala', 'Elixir', 'Erlang', 'SQL',
    'MySQL', 'PostgreSQL', 'SQLite', 'MongoDB', 'Redis', 'GraphQL', 'Docker', 'Kubernetes',
    'AWS', 'GCP', 'Azure', 'Terraform', 'Ansible', 'Puppet', 'Chef', 'Linux', 'Bash', 'PowerShell',
    'HTML', 'CSS', 'Saas', 'LESS', 'TypeScript', 'Webpack', 'Gulp', 'Grunt', 'Jenkins', 'CI/CD',
    'Machine Learning', 'Data Science', 'AI', 'Big Data', 'Hadoop', 'Spark', 'TensorFlow', 'PyTorch',
    'BI', 'KPIs', 'GIT'
}
tech_stacks_lower = {tech.lower() for tech in tech_stacks}

# Function to extract technology stacks from text
def extract_tech_stacks(text):
    identified_tech_stacks = set()

    # Regex to match words starting with uppercase letter
    pattern = r'\b[A-Z][a-zA-Z0-9+.-]*\b'
    words = re.findall(pattern, text)
    for word in words:
        if word.lower() in tech_stacks_lower:
            identified_tech_stacks.add(word)
    return identified_tech_stacks

# Function to extract average annual salary from text
def extract_salary(text):
    salary = 'N/A'
    # Regex to match salary string like $Xk, $XK, $X,XXX
    pattern = r'[$-]\d{1,3}[kK,]\d*'
    identified_salary = re.findall(pattern, text)
    total_salary = 0
    valid_salary_count = 0
    for salary_str in identified_salary:
        salary_str = salary_str[1:] # Remove the '$' from the beginning
        if salary_str[-1] in 'kK':
            salary_value = int(salary_str[:-1]) # Remove 'k' or 'K' and convert to integer
        elif ',' in salary_str:
            salary_value = int(salary_str.split(',')[0]) # Remove ',' and convert to integer
        else:
            continue

        # Consider valid salary if its > 40 ($40k)
        if salary_value > 40:
            total_salary += salary_value
            valid_salary_count += 1

    # Calculate average salary if valid salaries are found
    if valid_salary_count > 0:
        average_salary = total_salary / valid_salary_count
        formatted_salary = '{:.1f}'.format(average_salary)
        left_part, right_part = formatted_salary.split('.')
        salary = '$' + left_part + ',' + right_part + '00' # Format salary as $XXX,XXX
    return salary