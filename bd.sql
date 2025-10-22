-- 1) Таблица библиотек
CREATE TABLE libraries (
    library_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    address TEXT NOT NULL,
    phone VARCHAR(20) UNIQUE
);

-- 2) Тематики
CREATE TABLE themes (
    theme_id SERIAL PRIMARY KEY,
    theme_name VARCHAR(100) NOT NULL UNIQUE
);

-- 3) Книги
CREATE TABLE books (
    book_id SERIAL PRIMARY KEY,
    library_id INT NOT NULL REFERENCES libraries(library_id) ON DELETE CASCADE,
    theme_id INT REFERENCES themes(theme_id) ON DELETE SET NULL,
    author VARCHAR(100) NOT NULL,
    title VARCHAR(150) NOT NULL,
    publisher VARCHAR(100),
    publish_place VARCHAR(100),
    publish_year INT CHECK (publish_year >= 1500 AND publish_year <= EXTRACT(YEAR FROM CURRENT_DATE)),
    quantity INT DEFAULT 1 CHECK (quantity >= 0)
);

-- 4) Читатели
CREATE TABLE readers (
    reader_id SERIAL PRIMARY KEY,
    full_name VARCHAR(150) NOT NULL,
    address TEXT,
    phone VARCHAR(20) UNIQUE
);

-- 5) Абонементы (выдача книг)
CREATE TABLE subscriptions (
    sub_id SERIAL PRIMARY KEY,
    book_id INT NOT NULL REFERENCES books(book_id) ON DELETE CASCADE,
    reader_id INT NOT NULL REFERENCES readers(reader_id) ON DELETE CASCADE,
    give_date DATE DEFAULT CURRENT_DATE,
    return_date DATE,
    prepayment NUMERIC(10,2) DEFAULT 0 CHECK (prepayment >= 0)
);

-- 6) Сотрудники
CREATE TABLE employees (
    employee_id SERIAL PRIMARY KEY,
    library_id INT NOT NULL REFERENCES libraries(library_id) ON DELETE CASCADE,
    full_name VARCHAR(150) NOT NULL,
    position VARCHAR(100) NOT NULL,
    hire_date DATE DEFAULT CURRENT_DATE
);

-- индексы
CREATE INDEX idx_books_title ON books(title);
CREATE INDEX idx_subscriptions_dates ON subscriptions(give_date, return_date);

-- представление
CREATE VIEW v_books_basic AS
SELECT title, author, publish_year FROM books;

CREATE VIEW v_books_with_themes AS
SELECT b.title, b.author, t.theme_name, l.name as library
FROM books b
JOIN themes t ON b.theme_id = t.theme_id
JOIN libraries l ON b.library_id = l.library_id;

CREATE VIEW v_lib_book_counts AS
SELECT l.name, COUNT(b.book_id) AS book_count
FROM libraries l
JOIN books b ON l.library_id = b.library_id
GROUP BY l.name
HAVING COUNT(b.book_id) > 5;


-- тригер

CREATE OR REPLACE FUNCTION decrease_book_quantity()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE books
    SET quantity = quantity - 1
    WHERE book_id = NEW.book_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_book_issue
AFTER INSERT ON subscriptions
FOR EACH ROW
EXECUTE FUNCTION decrease_book_quantity();
