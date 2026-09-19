#!/usr/bin/env python3
"""One-shot: tag name pools by community + gender, load a large REAL Indian name set,
drop any cross-community (unreal) UNUSED identities, and materialise fresh
within-community identities. Run on a box that can reach the controller DB:

    sudo /var/www/html/magzter-v3/venv/bin/python3 load_names.py [N]

N = how many identities to generate now (default 5000). Idempotent + safe to re-run:
names upsert by community, only UNUSED identities are ever deleted (reserved/used are
never touched), and generation only ADDS never-used within-community pairs.
"""
import sys
import psycopg2.extras
import db

N = int(sys.argv[1]) if len(sys.argv) > 1 else 5000

# ── REAL name set, grouped by community. First names carry gender (M/F/U); surnames are
#    gender-neutral. Kept deliberately within-community so every pair looks real. ──────
HINDU_M = """Aarav Aditya Akash Aman Amit Anand Anil Ankit Ankur Anuj Arjun Arun Ashish
Ashok Ayush Chirag Deepak Dev Dhruv Gaurav Girish Harsh Hemant Hitesh Jatin Kabir Karan
Kunal Lakshya Manish Mayank Mohit Mukesh Naveen Nikhil Nitin Pankaj Parth Piyush Prakash
Pranav Prateek Praveen Rahul Raj Rajat Rajesh Rakesh Ravi Rohan Rohit Sagar Sachin Sandeep
Sanjay Saurabh Shekhar Shivam Shubham Siddharth Sumit Sunil Suresh Tarun Uday Varun Vijay
Vikas Vikram Vinay Vishal Yash Yogesh Ansh""".split()
HINDU_F = """Aarti Aditi Akanksha Ananya Anjali Anita Anushka Aparna Bhavna Deepa Deepika
Divya Ekta Gauri Geeta Isha Jyoti Kajal Kavya Komal Kritika Lakshmi Madhuri Manisha Meera
Meghna Nandini Neha Nidhi Nikita Pallavi Payal Pooja Prachi Preeti Priya Priyanka Radha
Rashmi Riya Sakshi Sarika Seema Shalini Shreya Shruti Sneha Sonam Sonia Suman Sunita Swati
Tanvi Tanya Trisha Vaishnavi Vandana Varsha""".split()
HINDU_L = """Agarwal Aggarwal Ahuja Arora Bajaj Bansal Bhardwaj Bhat Bhatia Bhatt Chauhan
Chaudhary Chatterjee Chopra Das Dixit Dubey Dutta Gandhi Ghosh Goel Goswami Gupta Iyer Jain
Jha Joshi Kapoor Kaul Khanna Kohli Kulkarni Kumar Malhotra Mehra Mehta Menon Mishra Mittal
Mukherjee Nair Nayak Pandey Patel Pillai Prasad Rana Rao Rawat Reddy Roy Saini Saxena
Sengupta Sethi Shah Sharma Shetty Shukla Singh Sinha Srivastava Tandon Thakur Tiwari Trivedi
Varma Verma Yadav""".split()

MUSLIM_M = """Aamir Abdul Adnan Ahmed Ali Altaf Amir Arif Asif Ayaan Bilal Danish Faisal
Faizan Farhan Fardeen Hamza Haris Imran Irfan Junaid Kaif Kamran Khalid Mohammed Mohsin Moin
Nadeem Naseer Nawaz Rehan Riyaz Saad Salman Sameer Shahid Shoaib Sohail Tariq Wasim Yusuf
Zaid Zeeshan Zubair""".split()
MUSLIM_F = """Aaliya Afreen Alia Amina Ayesha Bushra Farah Fatima Gazala Heena Hina Iram
Nazia Nida Noor Rabia Rehana Rukhsar Saba Sadia Saira Salma Sana Shabana Shaista Sofia
Tabassum Yasmin Zainab Zara Zeenat Zoya""".split()
MUSLIM_L = """Ahmed Akhtar Ali Ansari Aziz Baig Chishti Farooqui Hashmi Hussain Idrisi Iqbal
Khan Malik Mansoori Mirza Momin Pathan Qureshi Rangrez Rizvi Saifi Sayyed Sheikh Siddiqui
Syed Usmani Warsi Zaidi""".split()

SIKH_M = """Amandeep Amrit Arjan Balwinder Charanjit Daljeet Gagandeep Gurdeep Gurmeet
Gurpreet Harjinder Harpreet Inderjeet Jaskaran Jaspreet Jatinder Kuldeep Mandeep Manjot
Navdeep Navjot Paramjit Parminder Prabhjot Ranjit Sarabjit Sukhdeep Sukhwinder Tejinder""".split()
SIKH_F = """Amanpreet Baljeet Gurleen Harleen Ishmeet Jasleen Kiranjit Kirandeep Manpreet
Navneet Prabhleen Rajwinder Ramanjot Ravneet Simran Sukhmani Sukhpreet Jasmeet Manjeet""".split()
SIKH_L = """Ahluwalia Bajwa Bedi Brar Chahal Cheema Dhaliwal Dhillon Gill Grewal Kang Khalsa
Mann Nagra Randhawa Sandhu Sekhon Sidhu Sodhi Toor Virk""".split()

CHRIST_M = """Aaron Alan Albert Alex Allen Benjamin Brian Christopher Clement Daniel David
Dennis Edwin Ethan Franklin Gerald Ivan Jacob James Jason John Joseph Joshua Kevin Leon Mark
Nathan Nicholas Peter Philip Richard Robert Ryan Samuel Stephen Thomas Vincent""".split()
CHRIST_F = """Angela Annie Bella Caroline Catherine Christina Clara Diana Elizabeth Emily
Fiona Grace Helen Irene Jennifer Jessica Joanna Julia Linda Lisa Maria Mary Michelle Monica
Nancy Natasha Nicole Olivia Rachel Rebecca Rose Sandra Sarah Sharon Sophia Stella Teresa
Veronica""".split()
CHRIST_L = """Almeida Andrade Baptista Barretto Braganza Coelho Costa Cardoso Colaco Cruz
Dias Fernandes Fernandez Furtado George Gomes Gonsalves Jacob John Joseph Lobo Menezes Mathew
Mascarenhas Monteiro Nazareth Noronha Pereira Pinto Rebello Rodrigues Saldanha Sequeira
Thomas Vaz""".split()

FIRSTS = ([(n, "Hindu", "M") for n in HINDU_M] + [(n, "Hindu", "F") for n in HINDU_F] +
          [(n, "Muslim", "M") for n in MUSLIM_M] + [(n, "Muslim", "F") for n in MUSLIM_F] +
          [(n, "Sikh", "M") for n in SIKH_M] + [(n, "Sikh", "F") for n in SIKH_F] +
          [(n, "Christian", "M") for n in CHRIST_M] + [(n, "Christian", "F") for n in CHRIST_F])
LASTS = ([(n, "Hindu") for n in HINDU_L] + [(n, "Muslim") for n in MUSLIM_L] +
         [(n, "Sikh") for n in SIKH_L] + [(n, "Christian") for n in CHRIST_L])


def main():
    conn = db._conn()
    cur = conn.cursor()

    # 1) schema: community + gender tags (additive, idempotent)
    cur.execute("ALTER TABLE first_names ADD COLUMN IF NOT EXISTS community text")
    cur.execute("ALTER TABLE first_names ADD COLUMN IF NOT EXISTS gender text")
    cur.execute("ALTER TABLE last_names  ADD COLUMN IF NOT EXISTS community text")
    conn.commit()

    # 2) upsert names WITH tags (also re-tags the existing 40+30 correctly)
    psycopg2.extras.execute_values(cur,
        "INSERT INTO first_names (name, community, gender) VALUES %s "
        "ON CONFLICT (name) DO UPDATE SET community=EXCLUDED.community, gender=EXCLUDED.gender",
        FIRSTS)
    psycopg2.extras.execute_values(cur,
        "INSERT INTO last_names (name, community) VALUES %s "
        "ON CONFLICT (name) DO UPDATE SET community=EXCLUDED.community",
        LASTS)
    # any leftover untagged existing name -> Hindu (safe majority; known Muslim ones above
    # already got tagged by the upsert)
    cur.execute("UPDATE first_names SET community='Hindu' WHERE community IS NULL")
    cur.execute("UPDATE last_names  SET community='Hindu' WHERE community IS NULL")
    conn.commit()

    # 3) drop cross-community (unreal) UNUSED identities so they get replaced by real ones.
    #    reserved/used identities are in-flight/spent — never touched.
    cur.execute("""
        DELETE FROM identities i
         USING first_names f, last_names l
         WHERE i.first_name=f.name AND i.last_name=l.name
           AND f.community IS DISTINCT FROM l.community
           AND i.status='unused'
    """)
    dropped = cur.rowcount
    conn.commit()

    # capacity report (within-community)
    cur.execute("""
        SELECT COALESCE(SUM(cf*cl),0) FROM
             (SELECT community, count(*) cf FROM first_names GROUP BY community) f
        JOIN (SELECT community, count(*) cl FROM last_names  GROUP BY community) l USING (community)
    """)
    capacity = cur.fetchone()[0]
    cur.execute("SELECT community, count(*) FROM first_names GROUP BY community ORDER BY 2 DESC")
    fby = cur.fetchall()
    cur.execute("SELECT community, count(*) FROM last_names GROUP BY community ORDER BY 2 DESC")
    lby = cur.fetchall()
    print("first_names by community:", dict(fby))
    print("last_names  by community:", dict(lby))
    print("REAL within-community capacity:", capacity)
    print("dropped cross-community unused identities:", dropped)

    # 4) active campaign + generate N fresh within-community identities
    cur.execute("SELECT id FROM campaigns WHERE status='active' ORDER BY id DESC LIMIT 1")
    row = cur.fetchone()
    conn.close()
    if not row:
        print("no active campaign — names loaded, skipping generation")
        return
    cid = int(row[0])
    res = db.generate_identities(cid, N)
    print("generate_identities:", res)

    c = db._conn(); cur = c.cursor()
    cur.execute("SELECT status, count(*) FROM identities GROUP BY status ORDER BY 2 DESC")
    print("identities now:", dict(cur.fetchall()))
    c.close()


if __name__ == "__main__":
    main()
