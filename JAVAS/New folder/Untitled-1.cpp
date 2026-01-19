// electricity_system.cpp
// Dummy Electricity Bill Payment System (console-based)
// Compile: g++ -std=c++17 electricity_system.cpp -o electricity_system

#include <iostream>
#include <vector>
#include <string>
#include <iomanip>
#include <fstream>
#include <sstream>
#include <ctime>

using namespace std;

struct Customer {
    int id;
    string name;
    string address;
    int unitsConsumed;
    double amountDue;
    bool paid;
    string paymentDate; // empty if not paid
};

vector<Customer> customers;
int nextCustomerId = 1;
const string DATA_FILE = "customers.csv";

// Utility: current date as string YYYY-MM-DD
string today_date() {
    time_t t = time(nullptr);
    tm *lt = localtime(&t);
    char buf[20];
    strftime(buf, sizeof(buf), "%Y-%m-%d", lt);
    return string(buf);
}

// Calculate bill using a simple slab system:
// 0-100 units -> 1.50 per unit
// 101-200 units -> 2.50 per unit
// >200 units -> 4.00 per unit
// plus fixed charge 50
double calculate_bill(int units) {
    double amount = 0.0;
    int remaining = units;

    if (remaining <= 0) return 0.0;

    // first 100
    int slab = min(remaining, 100);
    amount += slab * 1.50;
    remaining -= slab;

    if (remaining > 0) {
        slab = min(remaining, 100);
        amount += slab * 2.50;
        remaining -= slab;
    }
    if (remaining > 0) {
        amount += remaining * 4.00;
        remaining = 0;
    }

    // fixed charge
    amount += 50.0;

    return amount;
}

void save_data() {
    ofstream fout(DATA_FILE);
    if (!fout) {
        cerr << "Warning: could not open " << DATA_FILE << " for writing.\n";
        return;
    }
    // CSV header
    fout << "id,name,address,units,amount,paid,paymentDate\n";
    for (auto &c: customers) {
        fout << c.id << ","
             << "\"" << string(c.name).replace(c.name.find("\""), 0, "") << "\","
             << "\"" << string(c.address).replace(c.address.find("\""), 0, "") << "\","
             << c.unitsConsumed << ","
             << fixed << setprecision(2) << c.amountDue << ","
             << (c.paid ? "1" : "0") << ","
             << c.paymentDate << "\n";
    }
    fout.close();
}

void load_data() {
    ifstream fin(DATA_FILE);
    if (!fin) return; // no file yet
    string line;
    getline(fin, line); // header
    customers.clear();
    int maxId = 0;
    while (getline(fin, line)) {
        if (line.empty()) continue;
        // Very simple CSV parsing (assuming no embedded commas in fields for now)
        // Format: id,name,address,units,amount,paid,paymentDate
        stringstream ss(line);
        string item;
        vector<string> cols;
        while (getline(ss, item, ',')) cols.push_back(item);

        // If the CSV had quotes or commas in fields this would need robust parsing.
        if (cols.size() < 7) continue;

        Customer c;
        c.id = stoi(cols[0]);
        // Remove surrounding quotes if any
        auto strip_quotes = [](string s)->string {
            if (!s.empty() && s.front() == '"' && s.back() == '"') return s.substr(1, s.size()-2);
            return s;
        };
        c.name = strip_quotes(cols[1]);
        c.address = strip_quotes(cols[2]);
        c.unitsConsumed = stoi(cols[3]);
        c.amountDue = stod(cols[4]);
        c.paid = (cols[5] == "1");
        c.paymentDate = cols[6];

        customers.push_back(c);
        if (c.id > maxId) maxId = c.id;
    }
    nextCustomerId = maxId + 1;
    fin.close();
}

// Menu actions
void add_customer() {
    Customer c;
    c.id = nextCustomerId++;
    cout << "Enter customer name: ";
    getline(cin, c.name);
    if (c.name.empty()) {
        cout << "Name cannot be empty. Aborting.\n";
        return;
    }
    cout << "Enter address: ";
    getline(cin, c.address);
    int units = 0;
    cout << "Enter units consumed (integer): ";
    while (!(cin >> units) || units < 0) {
        cout << "Please enter a valid non-negative integer for units: ";
        cin.clear();
        cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
    }
    cin.ignore(numeric_limits<streamsize>::max(), '\n');
    c.unitsConsumed = units;
    c.amountDue = calculate_bill(units);
    c.paid = false;
    c.paymentDate = "";
    customers.push_back(c);
    cout << "Customer added with ID #" << c.id << ". Amount due: " << fixed << setprecision(2) << c.amountDue << "\n";
    save_data();
}

Customer* find_customer_by_id(int id) {
    for (auto &c : customers) if (c.id == id) return &c;
    return nullptr;
}

void generate_bill() {
    cout << "Enter customer ID: ";
    int id; 
    while (!(cin >> id)) {
        cout << "Enter a valid numeric ID: ";
        cin.clear();
        cin.ignore(numeric_limits<streamsize>::max(), '\n');
    }
    cin.ignore(numeric_limits<streamsize>::max(), '\n');
    Customer* c = find_customer_by_id(id);
    if (!c) {
        cout << "Customer not found.\n";
        return;
    }
    cout << "\n--- Bill for Customer ID #" << c->id << " ---\n";
    cout << "Name    : " << c->name << "\n";
    cout << "Address : " << c->address << "\n";
    cout << "Units   : " << c->unitsConsumed << "\n";
    cout << "Amount  : ₹" << fixed << setprecision(2) << c->amountDue << "\n";
    cout << "Status  : " << (c->paid ? ("PAID on " + c->paymentDate) : "UNPAID") << "\n";
    cout << "-------------------------------\n";
}

void pay_bill() {
    cout << "Enter customer ID to pay: ";
    int id;
    while (!(cin >> id)) {
        cout << "Enter a valid numeric ID: ";
        cin.clear();
        cin.ignore(numeric_limits<streamsize>::max(), '\n');
    }
    cin.ignore(numeric_limits<streamsize>::max(), '\n');
    Customer* c = find_customer_by_id(id);
    if (!c) {
        cout << "Customer not found.\n";
        return;
    }
    if (c->paid) {
        cout << "This bill is already marked paid (on " << c->paymentDate << ").\n";
        return;
    }
    cout << "Amount to pay: ₹" << fixed << setprecision(2) << c->amountDue << "\n";
    cout << "Confirm payment? (y/n): ";
    char ch;
    cin >> ch;
    cin.ignore(numeric_limits<streamsize>::max(), '\n');
    if (ch == 'y' || ch == 'Y') {
        c->paid = true;
        c->paymentDate = today_date();
        cout << "Payment successful. Recorded on " << c->paymentDate << ".\n";
        save_data();
    } else {
        cout << "Payment cancelled.\n";
    }
}

void view_all_customers() {
    if (customers.empty()) {
        cout << "No customers present.\n";
        return;
    }
    cout << left << setw(6) << "ID" << setw(20) << "Name" << setw(10) << "Units" 
         << setw(12) << "Amount" << setw(8) << "Paid" << setw(12) << "PayDate" << "\n";
    cout << string(70, '-') << "\n";
    for (auto &c : customers) {
        cout << setw(6) << c.id
             << setw(20) << c.name.substr(0, 19)
             << setw(10) << c.unitsConsumed
             << "₹" << setw(9) << fixed << setprecision(2) << c.amountDue
             << setw(8) << (c.paid ? "Yes" : "No")
             << setw(12) << c.paymentDate << "\n";
    }
}

void sample_data() {
    // Helpful for quick demo
    Customer a{nextCustomerId++, "Ram Kumar", "Village Road 12", 120, 0.0, false, ""};
    a.amountDue = calculate_bill(a.unitsConsumed);
    Customer b{nextCustomerId++, "Sita Devi", "Green Street", 250, 0.0, false, ""};
    b.amountDue = calculate_bill(b.unitsConsumed);
    customers.push_back(a);
    customers.push_back(b);
    save_data();
    cout << "Sample data added.\n";
}

void show_menu() {
    cout << "\n===== Electricity Bill Payment System =====\n";
    cout << "1. Add Customer & Generate Bill\n";
    cout << "2. View Bill by Customer ID\n";
    cout << "3. Pay Bill\n";
    cout << "4. View All Customers\n";
    cout << "5. Add Sample Demo Data\n";
    cout << "0. Exit\n";
    cout << "Choose an option: ";
}

int main() {
    load_data();
    cout << "Welcome to the Dummy Electricity Bill Payment System\n";
    while (true) {
        show_menu();
        int choice;
        if (!(cin >> choice)) {
            cout << "Please enter a valid number.\n";
            cin.clear();
            cin.ignore(numeric_limits<streamsize>::max(), '\n');
            continue;
        }
        cin.ignore(numeric_limits<streamsize>::max(), '\n'); // flush newline
        switch (choice) {
            case 1: add_customer(); break;
            case 2: generate_bill(); break;
            case 3: pay_bill(); break;
            case 4: view_all_customers(); break;
            case 5: sample_data(); break;
            case 0:
                cout << "Exiting. Goodbye!\n";
                save_data();
                return 0;
            default:
                cout << "Invalid choice.\n";
        }
    }
    return 0;
}
