# SQLModel Schema Generator Skill

## Purpose
Generate SQLModel database models from data specifications with proper relationships, validations, and indexes.

## When to Use
- Creating database models from specs
- Adding new tables to existing schema
- Defining relationships between models
- Adding indexes and constraints

## Prerequisites
- Neon DB configured (use Neon DB Setup skill)
- Data model specification ready
- SQLModel installed

## Instructions

### Step 1: Read Data Model Specification
Review the spec to identify:
- Tables/Models needed
- Fields and their types
- Required vs optional fields
- Relationships (one-to-many, many-to-many)
- Unique constraints
- Indexes needed

### Step 2: Create Models File
See [models.md](models.md)

### Step 3: Add Field Validations
See [validations.md](validations.md)

### Step 4: Add Indexes
See [models.md](models.md)

### Step 5: Create Pydantic Schemas
See [validations.md](validations.md)

### Step 6: Initialize Database
See [models.md](models.md)

## Relationships
See [relationships.md](relationships.md)

## Validation Checklist
- [ ] All models inherit from `SQLModel` with `table=True`
- [ ] Primary keys defined correctly
- [ ] Foreign keys reference existing tables
- [ ] Relationships defined with `back_populates`
- [ ] Indexes added for frequently queried fields
- [ ] Required fields don't have `Optional` type
- [ ] Timestamps use `datetime.utcnow` default
- [ ] String fields have max_length constraints
- [ ] Create/Update/Read schemas defined

## Output Files
- `backend/models.py` - Database models
- `backend/schemas.py` (optional) - Separate Pydantic schemas

## Next Steps
After creating models:
1. Use **Database Migration Manager** skill to apply schema
2. Use **REST API Generator** skill to create CRUD endpoints
3. Test models with sample data
