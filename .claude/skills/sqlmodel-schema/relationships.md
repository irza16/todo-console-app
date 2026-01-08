# SQLModel Relationships

## One-to-Many Relationship
```python
class Parent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

    # Relationship
    children: List["Child"] = Relationship(back_populates="parent")

class Child(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    parent_id: int = Field(foreign_key="parent.id")
    name: str

    # Relationship
    parent: Parent = Relationship(back_populates="children")
```

## Many-to-Many Relationship
```python
class StudentCourseLink(SQLModel, table=True):
    __tablename__ = "student_course_link"
    student_id: int = Field(foreign_key="student.id", primary_key=True)
    course_id: int = Field(foreign_key="course.id", primary_key=True)

class Student(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    courses: List["Course"] = Relationship(
        back_populates="students",
        link_model=StudentCourseLink
    )

class Course(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    students: List[Student] = Relationship(
        back_populates="courses",
        link_model=StudentCourseLink
    )
```

## Relationship Validation Checklist
- [ ] Foreign keys reference existing tables
- [ ] Relationships defined with `back_populates`
- [ ] Indexes added on foreign key columns
- [ ] Link model for many-to-many relationships
