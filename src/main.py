import streamlit as st
import requests
from bs4 import BeautifulSoup as bs
from extractors import extract_tech_stacks, extract_salary
import regex as re

# Function to fetch jobs from We Work Remotely
def fetch_jobs():
    url = 'https://weworkremotely.com'
    response = requests.get(url)
    web_content = bs(response.content, 'html.parser')

    jobs = {}
    # Iterate over sections (different categories) containing job listings
    for section in web_content.find_all('section', class_='jobs'):
        category_name = section.h2.a.text.strip()
        ul = section.ul

        # Check for 'view-all' option to load more jobs
        can_see_more = section.find('li', class_='view-all')
        if can_see_more:
            sub_link = can_see_more.a.get('href')
            response = requests.get(url + str(sub_link))
            web_content = bs(response.content, 'html.parser')
            section = web_content.find('section', class_='jobs')
            ul = section.ul

        # Iterate over each job listing in the section
        for li in ul.find_all('li', recursive=False):
            a_tags = li.find_all('a')
            if len(a_tags) > 1:
                span_tags = a_tags[1].find_all('span', recursive=False)
                region_span = li.find('span', class_='region company')
                company_name = span_tags[0].text
                job_title = li.find('span', class_='title').text
                job_offer_link = a_tags[1].get('href')
                job_region = region_span.text if region_span else 'N/A'

                # Extract logo URL if available
                logo_url = ''
                div_logo = li.find('div', class_='flag-logo')
                if div_logo:
                    style_attr = div_logo.get('style')
                    if style_attr:
                        match = re.search(r"url\((.*?)\)", style_attr)
                        if match:
                            logo_url = match.group(1).strip("'\"")

                # Fetch detailed job content from job offer link
                response = requests.get(url + str(job_offer_link))
                web_content = bs(response.content, 'html.parser')
                listing_container = web_content.find('div', class_='listing-container')
                header_container = web_content.find('div', class_='listing-header-container')
                identified_tech_stack = set()
                salary = 'N/A'

                # Extract tech stack and salary from job description
                if listing_container and header_container:
                    combined_content = listing_container.get_text() + " " + header_container.get_text()
                    identified_tech_stack = extract_tech_stacks(combined_content)
                    salary = extract_salary(combined_content)

                # Store job details in dictionary
                job = {
                    'companyName': company_name,
                    'jobTitle': job_title,
                    'techStack': identified_tech_stack,
                    'salary': salary,
                    'jobRegion': job_region,
                    'jobUrl': url + job_offer_link,
                    'logoUrl': logo_url,
                }
                if category_name in jobs:
                    jobs[category_name].append(job)
                else:
                    jobs[category_name] = [job]

    return jobs

# Main function to display fetched jobs using Streamlit
def main():
    st.title('Remote Jobs Listing')
    st.header('Scraped from We Work Remotely')

    if 'jobs' not in st.session_state:
        st.session_state.jobs = {} # Define variable that would be accessible across different returns of Streamlit app

    # Button to trigger job fetching
    if st.button('Fetch Data'):
        with st.spinner('Fetching jobs (this might take a while)...'):
            st.session_state.jobs = fetch_jobs()

    jobs = st.session_state.jobs

    if jobs:
        # Extract categories and tech stacks for filtering
        categories = list(jobs.keys())
        tech_stacks = set()
        for job_list in jobs.values():
            for job in job_list:
                tech_stacks.update(job['techStack'])

        # Filters
        selected_category = st.selectbox('Select Category', ['All'] + categories)
        selected_tech_stacks = st.multiselect('Select Tech Stacks', sorted(tech_stacks))

        # Filter jobs based on selections
        filtered_jobs = {}
        for category_name, job_list in jobs.items():
            if selected_category != 'All' and category_name != selected_category:
                continue
            filtered_list = []
            for job in job_list:
                # If no tech stacks are selected, or at least one tech stack matches, append job to filtered_list
                if not selected_tech_stacks or any(
                        tech_stack in job['techStack'] for tech_stack in selected_tech_stacks):
                    filtered_list.append(job)
            if filtered_list:
                filtered_jobs[category_name] = filtered_list

        # Display jobs categorized by category name
        for category_name, job_list in filtered_jobs.items():
            st.markdown(
                "<hr style='border: none; border-top: 1px solid #ccc; height: 2px; background-color: #ccc;'>",
                unsafe_allow_html=True)
            st.markdown(f"## {category_name}")
            st.markdown(
                "<hr style='border: none; border-top: 1px solid #ccc; height: 2px; background-color: #ccc;'>",
                unsafe_allow_html=True)
            for job in job_list:
                # Create a row with two columns for each job listing
                col1, col2 = st.columns([1, 4])

                # Display company logo if available
                if 'logoUrl' in job and job['logoUrl']:
                    with col1:
                        st.image(job['logoUrl'], width=80)

                # Display job title, company name, tech stack, region, salary, and job link
                with col2:
                    st.markdown(f"### {job['jobTitle']}")
                    st.markdown(f"##### {job['companyName']}")
                    if job.get('techStack'):
                        st.markdown("---")
                        st.markdown(', '.join(job['techStack']))
                        st.markdown("---")
                    st.markdown(f"**Region:** {job['jobRegion']}")
                    if job.get('salary') != 'N/A':
                        st.markdown(f"**Salary:** {job['salary']}")
                    st.markdown(f"[**More Info:**]({job['jobUrl']})")

                    # Horizontal line to separate each job offer
                    st.markdown("<hr style='border: none; border-top: 1px solid #ccc; height: 1px; background-color: #ccc;'>", unsafe_allow_html=True)

    else:
        st.write('No jobs found.')

if __name__ == '__main__':
    main()