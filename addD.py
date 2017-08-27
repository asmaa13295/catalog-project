from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dataBase_setup import Cat, Base, Item

engine = create_engine('sqlite:///catalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# Menu for Cupcake
Cupcake = Cat(name="Cupcake")
session.add(Cupcake)
session.commit()

item1 = Item(name="Apple Cinnamon", description="Enjoy a mouthful of tiny bits of apple topped with our delicious brown -sugar cream cheese icing and sprinkled cinnamon.", price="$7.50", cat_id=1)
session.add(item1)
session.commit()

item2 = Item(name="Birthday Cupcake", description=" Celebrate your birthday with our vanilla rainbow cake topped with milk chocolate and maltesers.", price="$8.50", cat_id=1)
session.add(item2)
session.commit()

item3 = Item(name="Blackberry Chunks", description="Add flavor to your day with this one- baked with our vanilla batter and topped with buttercream with cheese and blackberries.", price="$7", cat_id=1)
session.add(item3)
session.commit()

item4 = Item(name="Chocolate", description="Enjoy 100% Belgian chocolate cupcake as it melts in your mouth.", price="$9", cat_id=1)
session.add(item4)
session.commit()

item5 = Item(name="Red Velvet", description="the perfect combination of our moist vanilla and chocolate batter, topped with cream cheese icing.", price="$15", cat_id=1)
session.add(item5)
session.commit()

item6 = Item(name="Tiramisu", description="For all the coffee lovers, moistened with coffee and topped with imported Italian mascarpone cheese icing.", price="$9", cat_id=1)
session.add(item6)
session.commit()

item7 = Item(name="Vanilla", description="Classic vanilla cake topped with buttercream icing.", price="6", cat_id=1)
session.add(item7)
session.commit()

item8 = Item(name="Gluten Free-Almond", description="Gluten Free almond cupcakes are delicious to enjoy even with your special diet. Order 25 hours in advance.", price="$13", cat_id=1)
session.add(item8)
session.commit()



# Menu for  Cronuts
Cronuts = Cat(name="Cronuts")
session.add(Cronuts)
session.commit()


item9 = Item(name="Blueberry", description="Treat yourself to our croissant-doughnut pastry filled with blueberry and topped with sugar.", price="$12", cat_id=2)
session.add(item9)
session.commit()

item10 = Item(name="Cream Cheese", description="Delight in our croissant-doughnut pastry filled with your famous cream cheese filling, topped with sugar, and crushed walnuts.", price="$11.5", cat_id=2)
session.add(item10)
session.commit()

item11 = Item(name="Nutella", description="Scrumptiously prepared croissant-doughnut pastry filled with Nutella, topped with Nutella and crushed hazelnuts.", price="$17", cat_id=2)
session.add(item11)
session.commit()

item12 = Item(name="Vanilla", description="Baked to perfection, croissant-doughnut pastry filled with vanilla and topped with pink pastry cream.", price="$9.5", cat_id=2)
session.add(item12)
session.commit()



# Menu for Cake Pops
CakePops = Cat(name="CakePops")
session.add(CakePops)
session.commit()


item13 = Item(name="Chocolate Cake Pops ", description="The chocolate shell gives way with a little snap to a moist and soft inside, like a brownie that melts in your mouth", price="$9", cat_id=3)
session.add(item13)
session.commit()

item14 = Item(name="Rainbow Cake Pops ", description="Rainbow cake pops are a huge hit with the kids covered in rainbow sprinkles and full of color and flavor in the center.", price="$8.5", cat_id=3)
session.add(item14)
session.commit()

item15 = Item(name="Oreo Cake Pops ", description="Bite into Oreo Cake Pops for a concentrated combination of chocolate vanilla and Oreos that melt in your mouth at once.", price="$11", cat_id=3)
session.add(item15)
session.commit()


# Menu for Bakery
Bakery = Cat(name="Bakery")
session.add(Bakery)
session.commit()


item16 = Item(name="Plain Croissant ", description="healthy and delisious baked croissant", price="$13.5", cat_id=4)
session.add(item16)
session.commit()

item17 = Item(name="Zaatar Croissant ", description="healthy and delisious baked croissant", price="$15", cat_id=4)
session.add(item17)
session.commit()

item18 = Item(name="Almond Croissant", description="healthy and delisious baked croissant", price="$12", cat_id=4)
session.add(item18)
session.commit()

item19 = Item(name="Paprika Pate", description="healthy and delisious baked croissant", price="$12", cat_id=4)
session.add(item19)
session.commit()